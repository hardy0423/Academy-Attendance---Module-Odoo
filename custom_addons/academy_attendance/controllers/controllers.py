# from odoo import http


# class AcademyAttendance(http.Controller):
#     @http.route('/academy_attendance/academy_attendance', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/academy_attendance/academy_attendance/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('academy_attendance.listing', {
#             'root': '/academy_attendance/academy_attendance',
#             'objects': http.request.env['academy_attendance.academy_attendance'].search([]),
#         })

#     @http.route('/academy_attendance/academy_attendance/objects/<model("academy_attendance.academy_attendance"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('academy_attendance.object', {
#             'object': obj
#         })

