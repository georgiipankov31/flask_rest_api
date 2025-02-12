import psycopg2.extras


logger_message_id = 0
class FDataBase:
    def __init__(self, con):
        self.__con = con
        self.__cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    def is_user_exists(self, username: str) -> bool:
        "Проверить существует ли пользователь"
        self.__cur.execute("""SELECT 1 FROM rest_app.users WHERE username = %s limit 1;""", (username,))
        res = self.__cur.fetchone()
        if not res:
            return False
        return True
    
    def auth_user_by_pswd(self, username:str, password:str) -> bool:
        "Проверка валидности пароля"
        self.__cur.execute("""SELECT 1 FROM rest_app.users WHERE username = %s AND password = %s limit 1;""", (username, password))
        res = self.__cur.fetchone()
        if not res:
            return False
        return True
    
    def post_user(self, username:str, password:str, role:str):
        "Добавить пользователя в базу"
        self.__cur.execute("""INSERT INTO rest_app.users (username, password, role) VALUES (%s, %s, %s)""", (username, password, role))
        return True
    
    def get_user(self, username:str, password:str):
        "Проверка валидности пароля"
        try:
            self.__cur.execute("""SELECT * FROM rest_app.users WHERE username = %s AND password = %s limit 1;""", (username, password))
            res = self.__cur.fetchone()
            if not res:
                return False
            return res
        except Exception as e:
            global logger_message_id
            logger_message_id += 1
            return False
    
    def get_article(self, article_id:int):
        "Получить статью из базы"
        try:
            self.__cur.execute("""SELECT *  FROM rest_app.articles WHERE id = %s LIMIT 1;""", (article_id,))
            res = self.__cur.fetchone()
            return res, {'status': 'ok'}
        except Exception as e:
            global logger_message_id
            logger_message_id += 1
            return False, {'logger_message_id': logger_message_id, 'msg': e, 'status': 'database_error'}

    def delete_article(self, article_id:int) -> int:
        "Удалить статью из базы"
        try:
            self.__cur.execute("""DELETE FROM rest_app.articles WHERE id = %s RETURNING id;""", (article_id,))
            res = self.__cur.fetchone()
            return res['id'], {'status': 'ok'}
        except Exception as e:
            global logger_message_id
            logger_message_id += 1
            return False, {'logger_message_id': logger_message_id, 'msg': e, 'status': 'database_error'}
    
    def put_article(self, article_id:int, title:str, value:str, privacy:str):
        "Изменить статью в базе"
        try:
            self.__cur.execute("""UPDATE rest_app.articles set title=%s, value=%s, privacy=%s WHERE id = %s RETURNING *;""", (title, value, privacy, article_id))
            res = self.__cur.fetchone()
            json_updated = {
            "id": res["id"],
            "title": res["title"],
            "value": res["value"],
            "privacy": res["privacy"],
            "author_id": res["insered_by"]
            }
            return json_updated, {'status': 'ok'}
        except Exception as e:
            global logger_message_id
            logger_message_id += 1
            return False, {'logger_message_id': logger_message_id, 'msg': e, 'status': 'database_error'}
    
    def post_article(self, title, value, privacy, author_id):
        "Добавить статью в базу"
        try:
            self.__cur.execute("""INSERT INTO rest_app.articles (title, value, privacy, insered_by) VALUES (%s, %s, %s, %s) RETURNING *;""", (title, value, privacy, author_id))
            res = self.__cur.fetchone()
            json_add = {
            "id": res["id"],
            "title": res["title"],
            "value": res["value"],
            "privacy": res["privacy"],
            "author_id": res["insered_by"]
            }
            return json_add, {'status': 'ok'}
        except Exception as e:
            global logger_message_id
            logger_message_id += 1
            return False, {'logger_message_id': logger_message_id, 'msg': e, 'status': 'database_error'}
    
    def get_article_list(self, secret_level:str):
        "Получить перечень статей"
        try:
            if secret_level == 'public':
                self.__cur.execute("""SELECT * FROM rest_app.articles WHERE privacy = 'public';""")
                res = self.__cur.fetchall()
            elif secret_level == 'need_login':
                self.__cur.execute("""SELECT * FROM rest_app.articles WHERE (privacy = 'public' or privacy = 'need_login');""")
                res = self.__cur.fetchall()
            else:
                self.__cur.execute("""SELECT * FROM rest_app.articles;""")
                res = self.__cur.fetchall()
            list_article = []
            for article in res:
                list_article.append(
                    {
                        "id": article["id"],
                        "title": article["title"],
                        "value": article["value"],
                        "privacy": article["privacy"],
                        "author_id": article["insered_by"]
                    }
                )
            return list_article, {'status': 'ok'}
        except Exception as e:
            global logger_message_id
            logger_message_id += 1
            return False, {'logger_message_id': logger_message_id, 'msg': e, 'status': 'database_error'}
