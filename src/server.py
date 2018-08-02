import tornado.ioloop
import tornado.web
import pymysql as mariadb
import pymysql.cursors

db = mariadb.connect(host="localhost",
                     user="root",
                     password="",
                     db="reports",
                     charset="utf8mb4",
                     cursorclass=pymysql.cursors.DictCursor)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("report.html")

    def post(self):
        name = self.get_argument("inputName")
        email = self.get_argument("inputEmail")
        description = self.get_argument("inputDescription")
        priority = int(self.get_argument("issuePriority"))

        with db.cursor() as cursor:
            sql = "INSERT INTO reports (name, email, description, priority) VALUES (%s, %s, %s, %s)"

            cursor.execute(sql, (name, email, description, priority))

        db.commit()

        self.write("Thank you for your report.")


class ReportHandler(tornado.web.RequestHandler):
    def get(self):
        items = []

        with db.cursor() as cursor:
            sql = "SELECT * FROM reports"
            cursor.execute(sql)

            for row in cursor.fetchmany(10):
                items.append([row["id"], row["priority"],
                              row["name"], row["email"], row["description"]])

        self.render("view_reports.html", items=items)


class IssueHandler(tornado.web.RequestHandler):
    def get(self, issue_number):
        with db.cursor() as cursor:
            sql = "SELECT * FROM reports WHERE id=%s"
            cursor.execute(sql, (issue_number,))

            if cursor.rowcount == 0:
                self.send_error(status_code=404)
            else:
                response = cursor.fetchone()
                self.render("view_issue.html", data=response)


def make_app():
    return tornado.web.Application([(r"/", MainHandler), (r"/view_reports", ReportHandler), (r"/issue/([0-9]+)", IssueHandler)])


app = make_app()
app.listen(8888)
tornado.ioloop.IOLoop.current().start()
