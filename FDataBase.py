import sqlite3

class FDataBase:
    def __init__(self, db) -> None:
        self.__db = db
        self.__cur = db.cursor()


    def getMenu(self):
        sql = 'select * from mainmenu'
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('error')
        return [] 
    



    def addPost(self, user_id, title, text, tags, img, date):
        try:
            binary = sqlite3.Binary(img)
            self.__cur.execute('insert into Posts values(null, ?, ?, ?, ?, ?, ?)', (user_id, title, text, ' '.join(tags), binary, date))

            for t in tags:
                self.__cur.execute(f'select count() as "count" from Tags where tag_text like ?', (t,))
                res = self.__cur.fetchone()
                if res['count'] > 0:
                    print(f'{t} already exist')
                else:
                    self.__cur.execute('insert into Tags values(null, ?)', (t, ))
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        
        return True
    
    def addComment(self, user_id, post_id, text, date):
        try:
            self.__cur.execute('insert into Comments values(null, ?, ?, ?, ?)', (user_id, post_id, text, date))
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        
        return True
    
    def addUser(self, username, email, psw, date):
        try:
            self.__cur.execute(f'select count() as "count" from Users where email like "{email}"')
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('error2')
                return False
            # print('error44')
            
            self.__cur.execute('insert into Users values (null, ?, ?, ?, null, ?)', (username, email, psw, date))
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        
        return True
    




    def getPost(self, post_id):
        try:
            self.__cur.execute(f'select * from Posts where post_id = {post_id} limit 1')
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print(e)

        return []

    def getPostsAnonce(self, sort):
        try:
            query = '''SELECT
                            Users.username AS "username",
                            Users.user_id AS "user_id",
                            Posts.post_id AS "post_id",
                            Posts.title AS "title",
                            Posts.post_content AS "content",
                            Posts.tags as 'tags', 
                            Posts.post_img AS "img",
                            Posts.date_posted AS "date",
                            COUNT(Comments.comment_id) AS "comment_count"
                        FROM
                            Posts
                        INNER JOIN
                            Users ON Users.user_id = Posts.user_id
                        LEFT JOIN
                            Comments ON Comments.post_id = Posts.post_id
                        GROUP BY
                            Users.username, Posts.post_id, Posts.title, Posts.post_content, Posts.post_img 
                        '''
            if next(iter(sort.keys()), None) == 'sort':
                if sort['sort'] == 'new':    
                    self.__cur.execute(query + 'ORDER BY Posts.date_posted DESC;')
                elif sort['sort'] == 'most_discussed':
                    self.__cur.execute(query + 'ORDER BY COUNT(Comments.comment_id) DESC;')
                elif sort['sort'] == "default":
                    self.__cur.execute(query + ';')
            elif next(iter(sort.keys()), None) == 'tag':
                tag = sort['tag'] 
                self.__cur.execute(f'''SELECT
                            Users.username AS "username",
                            Users.user_id AS "user_id",
                            Posts.post_id AS "post_id",
                            Posts.title AS "title",
                            Posts.post_content AS "content",
                            Posts.tags as 'tags',
                            Posts.post_img AS "img",
                            Posts.date_posted AS date,
                            COUNT(Comments.comment_id) AS "comment_count"
                        FROM
                            Posts
                        INNER JOIN
                            Users ON Users.user_id = Posts.user_id
                        LEFT JOIN
                            Comments ON Comments.post_id = Posts.post_id
                        WHERE 
                            Posts.tags LIKE "%{tag}%"
                        GROUP BY
                            Users.username, Posts.post_id, Posts.title, Posts.post_content, Posts.post_img 
                        ''')   
            else:
                self.__cur.execute(query + ';')
            res = self.__cur.fetchall()
            if res: 
                return res
        except sqlite3.Error as e:
            print(e)

        return []
    
    def getPostsAnoncSearch(self, title):
        try:
            self.__cur.execute(f'''SELECT
                                Users.username AS "username",
                                Users.user_id AS "user_id",
                                Posts.post_id AS "post_id",
                                Posts.title AS "title",
                                Posts.post_content AS "content",
                                Posts.tags as 'tags',
                                Posts.post_img AS "img",
                                Posts.date_posted AS date,
                                COUNT(Comments.comment_id) AS "comment_count"
                            FROM
                                Posts
                            INNER JOIN
                                Users ON Users.user_id = Posts.user_id
                            LEFT JOIN
                                Comments ON Comments.post_id = Posts.post_id
                            WHERE 
                                Posts.title LIKE "%{title}%"
                            GROUP BY
                                Users.username, Posts.post_id, Posts.title, Posts.post_content, Posts.post_img 
                            ''') 
            res = self.__cur.fetchall()
            if res: 
                return res
        except sqlite3.Error as e:
            print(e)

        return []
    
    def getComments(self, post):
        try:
            self.__cur.execute(f'''select Users.username as "user", Comments.comment_content as "comment_content" 
                               from Comments inner join Users on Users.user_id = Comments.user_id
                               where post_id = {post}''')
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print(e)

        return []
    
    def getUser(self, user_id):
        try: 
            self.__cur.execute(f'select * from Users where user_id = {user_id} limit 1')
            res = self.__cur.fetchone()
            if res: return res

        except sqlite3.Error as e:
            print(e)

        return []
    
    def getUserByEmail(self, email):
        try: 
            self.__cur.execute(f'select * from Users where email = "{email}" limit 1')
            res = self.__cur.fetchone()
            if res: return res

        except sqlite3.Error as e:
            print(e)

        return []

    def getImg(self, id):
        img_data = None
        try:
            self.__cur.execute(f'select post_img from Posts where post_id = {id} limit 1')
            img = self.__cur.fetchone()
            if img:
                img_data = img['post_img']
        except sqlite3.Error as e:
            print(e)
        return img_data
    
    def getAva(self, id):
        img_data = None
        try:
            self.__cur.execute(f'select avatar from Users where user_id = {id} limit 1')
            img = self.__cur.fetchone()
            if img:
                img_data = img['avatar']
        except sqlite3.Error as e:
            print(e)
        return img_data
    
    def getMyPosts(self, user_id):
        try: 
            self.__cur.execute(f'select * from Posts where user_id = {user_id}')
            res = self.__cur.fetchall()
            if res: return res

        except sqlite3.Error as e:
            print(e)

        return []
    
    def getTags(self):
        try: 
            self.__cur.execute(f'select * from Tags ORDER BY tag_text ASC')
            res = self.__cur.fetchall()
            if res: return res

        except sqlite3.Error as e:
            print(e)

        return []




    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        
        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f'update Users set avatar = ? where user_id = ?', (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        return True
    
    
    def updateUserInfo(self, user_id, name, email):       
        try:
            self.__cur.execute(f'update Users set username = ?, email = ? where user_id = ?', (name, email, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        return True
    
    def updatePostInfo(self, post_id, title, content, img):       
        try:
            if img:
                binary = sqlite3.Binary(img)
                self.__cur.execute(f'update Posts set title = ?, post_content = ?, post_img = ? where post_id = ?', (title, content, binary, post_id))
                self.__db.commit()
            else:
                self.__cur.execute(f'update Posts set title = ?, post_content = ? where post_id = ?', (title, content, post_id))
                self.__db.commit()
        except sqlite3.Error as e:
            print(e)
            return False
        return True
    

