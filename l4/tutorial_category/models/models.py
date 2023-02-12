# -*- coding: utf-8 -*-

from odoo import models, fields


class Tag(models.Model):
    _name = "tutorial.game.tag"
    _description = "Tag for Games"

    name = fields.Char("Tag Name", required=True)
    description = fields.Text("Description")


class Game(models.Model):
    _inherit = "tutorial.game"

    tag_ids = fields.Many2many("tutorial.game.tag", relation="tag_rel", string="Tags")
