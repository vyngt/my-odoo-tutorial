# -*- coding: utf-8 -*-
from odoo import http


class Games(http.Controller):
    @http.route("/tutorial/games")
    def list(self):
        Game = http.request.env["tutorial.game"]
        games = Game.search([])
        games = games.filtered(lambda g: g.hidden == False)
        return http.request.render(
            "tutorial.game_list_template",
            {"games": games},
        )
