class Brain:
    def __init__(self, board, player):
        self.board = board
        self.player = player

    def checks(self):
        print("*" * 50)
        print("tableau->foundation:")
        for card, tableau_pile, index in self.check_foundation_tableau():
            print("   ", card, tableau_pile, index)
        print("crape:", self.check_player_crapette_tableau())
        print("stock:", self.check_player_stock_tableau())
        print("space:")
        for tableau_pile, tableau_pile_dest in self.check_potential_space():
            print("   ", tableau_pile, tableau_pile_dest)

    def check_foundation_tableau(self):
        """Check which card from the foundation can potentially be put on the tableau

        Returns a list of (card, tableau_pile, index).
        """
        potential = []
        for tableau_pile in self.board.tableau_piles:
            for index, card in enumerate(tableau_pile):
                for foundation_pile in self.board.foundation_piles:
                    if foundation_pile.can_add_card(card, tableau_pile, self.player):
                        potential.append((card, tableau_pile, index))
        return potential

    def check_player_crapette_tableau(self):
        """Check if the card on the player crapette can potentially be put on the tableau"""
        crapette_pile = self.board.players_piles[self.player].crape
        if not crapette_pile:
            return False
        card = crapette_pile.top_card
        if not card.face_up:  # Don't cheat
            return False
        for foundation_pile in self.board.foundation_piles:
            if foundation_pile.can_add_card(card, crapette_pile, self.player):
                return True
        return False

    def check_player_stock_tableau(self):
        """Check if the card on the player stock can potentially be put on the tableau"""
        stock_pile = self.board.players_piles[self.player].stock
        if not stock_pile:
            return False
        card = stock_pile.top_card
        if not card.face_up:  # Don't cheat
            return False
        for foundation_pile in self.board.foundation_piles:
            if foundation_pile.can_add_card(card, stock_pile, self.player):
                return True
        return False

    def check_potential_space(self):
        """Check if any tableau pile can potentially go over another tableau pile

        Returns a list of (tableau_pile, tableau_pile_dest)
        """
        potential = []
        for tableau_pile in self.board.tableau_piles:
            if not tableau_pile:
                continue
            card = tableau_pile[0]
            for tableau_pile_dest in self.board.tableau_piles:
                if not tableau_pile_dest:
                    continue
                if card.is_same_color(tableau_pile_dest.top_card):
                    continue
                if card.rank != tableau_pile_dest.top_card.rank - 1:
                    continue
                potential.append((tableau_pile, tableau_pile_dest))
        return potential
