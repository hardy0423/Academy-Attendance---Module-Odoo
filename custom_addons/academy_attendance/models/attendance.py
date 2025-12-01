from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, time

class Attendance(models.Model):
    _name = 'academy.attendance'
    _description = 'Attendance Record'
    _inherit = ['mail.thread']
    
    name = fields.Char(
        string='Reference',
        default=lambda self: self.env['ir.sequence'].next_by_code('academy.attendance'),
        readonly=True
    )
    
    # Relations Many2one
    course_id = fields.Many2one(
        'academy.course',
        string='Course',
        required=True,
        ondelete='cascade'
    )
    
    student_id = fields.Many2one(
        'academy.student',
        string='Student',
        required=True,
        ondelete='cascade'
    )
    
    # Champs de date/heure
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today
    )
    
    start_time = fields.Datetime(
        string='Start Time',
        required=True,
        default=fields.Datetime.now
    )
    
    end_time = fields.Datetime(string='End Time')
    
    # Status avec sélection
    status = fields.Selection([
        ('draft', 'Draft'),
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused')
    ], string='Status', default='draft', tracking=True)
    
    # Champ Boolean pour présence rapide
    is_present = fields.Boolean(string='Present')
    
    notes = fields.Text(string='Notes')
    
    # Champs calculés
    duration = fields.Float(
        string='Duration (hours)',
        compute='_compute_duration',
        store=True
    )

    # =========================
    # Contraintes SQL
    # =========================
    _sql_constraints = [
        # Un étudiant ne peut avoir qu'un seul enregistrement par cours et par date
        ('unique_student_course_date', 'unique(course_id, student_id, date)',
         'This student already has an attendance record for this course on this date.'),
        
        # Vérifie que la date n’est pas dans le futur
        ('check_date', 'CHECK (date <= current_date)',
         'Attendance date cannot be in the future.'),
        
        # Vérifie que start_time est toujours rempli (utile si non null)
        ('check_start_time', 'CHECK (start_time IS NOT NULL)',
         'Start time must be set.')
    ]
    
    # Contraintes
    @api.constrains('student_id', 'course_id', 'date')
    def _check_unique_attendance(self):
        for attendance in self:
            duplicate = self.search([
                ('student_id', '=', attendance.student_id.id),
                ('course_id', '=', attendance.course_id.id),
                ('date', '=', attendance.date),
                ('id', '!=', attendance.id)
            ])
            if duplicate:
                raise ValidationError(_(
                    "Attendance for this student and course on this date already exists!"
                ))
    
    @api.constrains('start_time', 'end_time')
    def _check_time(self):
        for attendance in self:
            if attendance.end_time and attendance.start_time > attendance.end_time:
                raise ValidationError(_(
                    "Start time must be before end time!"
                ))
    
    # Champs calculés
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for attendance in self:
            if attendance.start_time and attendance.end_time:
                delta = attendance.end_time - attendance.start_time
                attendance.duration = delta.total_seconds() / 3600
            else:
                attendance.duration = 0.0
    
    # Automatisme
    @api.onchange('is_present')
    def _onchange_is_present(self):
        if self.is_present:
            self.status = 'present'
        else:
            self.status = 'absent'
    
    # Action pour marquer présent
    def action_mark_present(self):
        self.write({'status': 'present', 'is_present': True})
    
    def action_mark_absent(self):
        self.write({'status': 'absent', 'is_present': False})
    
    def action_mark_late(self):
        self.write({'status': 'late'})