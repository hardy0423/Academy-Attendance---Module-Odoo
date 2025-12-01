from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class Student(models.Model):
    _name = 'academy.student'
    _description = 'Student'
    _inherit = ['mail.thread']
    _rec_name = 'full_name'
    
    # Champs personnels - indépendants de res.partner
    student_code = fields.Char(
        string='Student ID',
        required=True,
        unique=True,
        tracking=True
    )
    
    first_name = fields.Char(
        string='First Name',
        required=True
    )
    
    last_name = fields.Char(
        string='Last Name',
        required=True
    )
    
    full_name = fields.Char(
        string='Full Name',
        compute='_compute_full_name',
        store=True
    )
    
    email = fields.Char(string='Email')
    
    phone = fields.Char(string='Phone')
    
    birth_date = fields.Date(string='Date of Birth')
    
    enrollment_date = fields.Date(
        string='Enrollment Date',
        default=fields.Date.today
    )
    
    # Relations Many2many vers les cours
    course_ids = fields.Many2many(
        'academy.course',
        'course_student_rel',
        'student_id',
        'course_id',
        string='Enrolled Courses'
    )
    
    # Relation One2many vers les présences
    attendance_ids = fields.One2many(
        'academy.attendance',
        'student_id',
        string='Attendance Records'
    )
    
    # Champs calculés
    attendance_rate = fields.Float(
        string='Attendance Rate (%)',
        compute='_compute_attendance_rate',
        store=True,
        digits=(5, 2),
        help="Percentage of attended sessions"
    )
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True
    )
    
    # Compteurs pour démo
    total_courses = fields.Integer(
        string='Total Courses',
        compute='_compute_total_courses',
        store=True
    )
    
    total_attended = fields.Integer(
        string='Attended Sessions',
        compute='_compute_attendance_stats',
        store=True
    )
    
    total_missed = fields.Integer(
        string='Missed Sessions',
        compute='_compute_attendance_stats',
        store=True
    )

    _sql_constraints = [
        ('unique_student_code', 'unique(student_code)', 'The Student code must be unique!')
    ]
    
    # Contraintes - CORRIGÉES
    @api.constrains('student_code')
    def _check_student_code(self):
        for student in self:
            if student.student_code:
                # Nettoyer le code (enlever les espaces)
                code = student.student_code.strip()
                # Vérifier qu'il contient au moins un caractère
                if not code:
                    raise ValidationError(_("Student code cannot be empty!"))
                # Accepter les codes avec lettres, chiffres et tirets/soulignés
                # Ex: "STU-001", "2024-001", etc.
                if not all(c.isalnum() or c in ['-', '_', '.'] for c in code):
                    raise ValidationError(_(
                        "Student code can only contain letters, numbers, hyphens, underscores and dots!"
                    ))
    
    @api.constrains('email')
    def _check_email(self):
        for student in self:
            if student.email and '@' not in student.email:
                raise ValidationError(_(
                    "Invalid email format! Please enter a valid email address."
                ))
    
    # Champs calculés
    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for student in self:
            student.full_name = f"{student.first_name or ''} {student.last_name or ''}".strip()
    
    @api.depends('attendance_ids', 'attendance_ids.status')
    def _compute_attendance_rate(self):
        for student in self:
            # Filtrer seulement les présences confirmées (pas brouillon)
            attendances = student.attendance_ids.filtered(lambda a: a.status != 'draft')
            if attendances:
                present = attendances.filtered(lambda a: a.status == 'present')
                student.attendance_rate = (len(present) / len(attendances)) * 100
            else:
                student.attendance_rate = 0.0
    
    @api.depends('attendance_ids', 'attendance_ids.status')
    def _compute_attendance_stats(self):
        for student in self:
            # Filtrer seulement les présences confirmées
            attendances = student.attendance_ids.filtered(lambda a: a.status != 'draft')
            if attendances:
                student.total_attended = len(attendances.filtered(lambda a: a.status == 'present'))
                student.total_missed = len(attendances.filtered(lambda a: a.status == 'absent'))
            else:
                student.total_attended = 0
                student.total_missed = 0
    
    @api.depends('course_ids')
    def _compute_total_courses(self):
        for student in self:
            student.total_courses = len(student.course_ids)
    
    # Automatisme
    @api.onchange('birth_date')
    def _onchange_birth_date(self):
        if self.birth_date:
            today = fields.Date.today()
            age = today.year - self.birth_date.year
            # Ajuster si l'anniversaire n'est pas encore passé cette année
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1
                
            if age < 18:
                return {
                    'warning': {
                        'title': _('Underage Student'),
                        'message': _('This student is under 18 years old.')
                    }
                }
            elif age > 65:
                return {
                    'warning': {
                        'title': _('Senior Student'),
                        'message': _('This student is over 65 years old.')
                    }
                }
    
    @api.onchange('first_name', 'last_name')
    def _onchange_name(self):
        """Suggestion d'email basé sur le nom"""
        if self.first_name and self.last_name and not self.email:
            # Créer un email suggéré
            first_initial = self.first_name[0].lower() if self.first_name else ''
            last_name_lower = self.last_name.lower().replace(' ', '') if self.last_name else ''
            if first_initial and last_name_lower:
                self.email = f"{first_initial}.{last_name_lower}@student.academy.com"
    
    # Méthodes d'action
    def action_view_attendances(self):
        """Action pour voir toutes les présences de l'étudiant"""
        self.ensure_one()
        return {
            'name': _('Attendances'),
            'type': 'ir.actions.act_window',
            'res_model': 'academy.attendance',
            'view_mode': 'tree,form,calendar',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id}
        }
    
    def action_view_courses(self):
        """Action pour voir tous les cours de l'étudiant"""
        self.ensure_one()
        return {
            'name': _('Courses'),
            'type': 'ir.actions.act_window',
            'res_model': 'academy.course',
            'view_mode': 'tree,form,kanban',
            'domain': [('student_ids', 'in', self.id)],
            'context': {'default_student_ids': [(4, self.id)]}
        }
    
    # Méthode de recherche améliorée
    def name_get(self):
        result = []
        for student in self:
            name = f"[{student.student_code}] {student.full_name}"
            result.append((student.id, name))
        return result
    
    # Méthode de création avec séquence
    @api.model
    def create(self, vals):
        # Générer un code étudiant automatique si non fourni
        if not vals.get('student_code'):
            sequence = self.env['ir.sequence'].next_by_code('academy.student.code') or 'STU000'
            vals['student_code'] = sequence
        
        # Mettre à jour le nom complet
        if 'first_name' in vals or 'last_name' in vals:
            first_name = vals.get('first_name', '')
            last_name = vals.get('last_name', '')
            vals['full_name'] = f"{first_name} {last_name}".strip()
        
        return super(Student, self).create(vals)
    
    def write(self, vals):
        # Mettre à jour le nom complet si prénom ou nom changent
        if 'first_name' in vals or 'last_name' in vals:
            for student in self:
                first_name = vals.get('first_name', student.first_name)
                last_name = vals.get('last_name', student.last_name)
                vals['full_name'] = f"{first_name} {last_name}".strip()
                break  # On break car on ne peut updater qu'un étudiant à la fois pour ce champ
        
        return super(Student, self).write(vals)