from odoo import models, fields,api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class Course(models.Model):
    _name = 'academy.course'
    _description = 'Course'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Course Name',
        required=True,
        tracking=True
    )
    code = fields.Char(
        string='Course Code',
        required=True,
        tracking=True
    )
    description = fields.Text(string='Description')
    teacher_id = fields.Many2one(
        'res.partner',
        string='Teacher',
        domain=[('is_teacher', '=', True)],
        tracking=True
    )
    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.today,
        required=True
    )
    end_date = fields.Date(string='End Date')
    duration_hours = fields.Float(
        string='Duration (hours)',
        default=1.0
    )
    
    # Relation One2many vers les étudiants inscrits
    student_ids = fields.Many2many(
        'academy.student',
        'course_student_rel',
        'course_id',
        'student_id',
        string='Enrolled Students'
    )
    
    # Relation One2many vers les présences
    attendance_ids = fields.One2many(
        'academy.attendance',
        'course_id',
        string='Attendance Records'
    )
    
    # Champs calculés
    student_count = fields.Integer(
        string='Number of Students',
        compute='_compute_student_count',
        store=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    color = fields.Integer(string='Color Index')
    _sql_constraints = [
        ('unique_course_code', 'unique(code)', 'The course code must be unique!')
    ]

      # Contraintes
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for course in self:
            if course.end_date and course.start_date > course.end_date:
                raise ValidationError(_(
                    "Start date must be before end date!"
                ))
    
    @api.constrains('duration_hours')
    def _check_duration(self):
        for course in self:
            if course.duration_hours <= 0:
                raise ValidationError(_(
                    "Duration must be positive!"
                ))
    
    # Champs calculés
    @api.depends('student_ids')
    def _compute_student_count(self):
        for course in self:
            course.student_count = len(course.student_ids)
    
    # Action pour confirmer le cours
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_start(self):
        self.write({'state': 'in_progress'})
    
    def action_complete(self):
        self.write({'state': 'completed'})
    
    # Automatisme avec onchange
    @api.onchange('duration_hours')
    def _onchange_duration(self):
        if self.duration_hours > 4:
            return {
                'warning': {
                    'title': 'Long Course Warning',
                    'message': 'This course is quite long. Consider adding breaks.'
                }
            }