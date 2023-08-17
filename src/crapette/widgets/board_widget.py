import typing

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout

from .card_widget import CardWidget, DEFAULT_FLIP_DURATION, DEFAULT_MOVE_DURATION
from .pile_widgets import PileWidget

if typing.TYPE_CHECKING:
    from crapette import game_manager
    from crapette.core.cards import Card

TRANSITION_DURATION = 0.5


class BoardWidget(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pile_widgets: list[PileWidget] = None
        self.card_widgets: dict[Card, CardWidget] = None

        self.game_manager = None
        self._do_layout_event = None

    def do_layout(self, *args, **kwargs):
        """Delay the layout computing to avoid visual lag."""
        if self._do_layout_event is not None:
            self._do_layout_event.cancel()

        super_do_layout = super().do_layout

        def real_do_layout(_dt):
            super_do_layout(*args, **kwargs)

            self.place_cards()
            if self.game_manager:
                # with contextlib.suppress(KeyError):  # KeyError on window initialization
                self.place_background_halo(self.game_manager.active_player)

        layout_delay_s = 0.2  # s
        self._do_layout_event = Clock.schedule_once(real_do_layout, layout_delay_s)

    def setup(self, game_manager: "game_manager.GameManager"):
        """Prepare and initialize the board for a new game."""
        self.app = App.get_running_app()
        self.ids = self.app.root.ids
        self.game_manager = game_manager

        self.board = self.game_manager.board
        self.setup_piles()
        self.setup_card_widgets()
        self.place_cards()
        self.update_counts()

    def setup_piles(self):
        """Configure the piles.

        Configures the relation between the pile widgets and the backend piles, and
        updates the `pile_widgets` list.
        """
        self.pile_widgets = []
        for player, player_piles in enumerate(self.board.players_piles):
            self.pile_widgets.append(self.ids[f"player{player}stock"])
            self.pile_widgets.append(self.ids[f"player{player}waste"])
            self.pile_widgets.append(self.ids[f"player{player}crape"])
            self.ids[f"player{player}stock"].set_pile(player_piles.stock)
            self.ids[f"player{player}waste"].set_pile(player_piles.waste)
            self.ids[f"player{player}crape"].set_pile(player_piles.crape)
        for tableau, tableau_pile in enumerate(self.board.tableau_piles):
            self.pile_widgets.append(self.ids[f"tableau{tableau}"])
            self.ids[f"tableau{tableau}"].set_pile(tableau_pile)
        for foundation, foundation_pile in enumerate(self.board.foundation_piles):
            self.pile_widgets.append(self.ids[f"foundation{foundation}"])
            self.ids[f"foundation{foundation}"].set_pile(foundation_pile)

    def setup_card_widgets(self):
        """Create and add a widget for every card.

        Updates the `card_widgets` list.

        The cards are not placed on the board, see `place_cards`.
        """
        # Remove previous card widgets
        if self.card_widgets:
            for card_widget in self.card_widgets.values():
                self.app.root.remove_widget(card_widget)

        # Add all card widgets
        self.card_widgets = {}
        for pile_widget in self.pile_widgets:
            for card in pile_widget.pile:
                card_widget = CardWidget(card, self.game_manager)
                card_widget.pile_widget = pile_widget
                self.card_widgets[card] = card_widget
                self.app.root.add_widget(card_widget)

    def place_cards(self):
        """Reset the card widget positions in the piles."""
        if not self.pile_widgets:
            return
        for pile_widget in self.pile_widgets:
            for index, card in enumerate(pile_widget.pile):
                card_widget = self.card_widgets[card]
                card_widget.center = pile_widget.card_pos(index)

    def update_counts(self):
        """Update displayed card counts."""
        for player in range(self.board.NB_PLAYERS):
            stock_pile = self.ids[f"player{player}stock"].pile
            crape_pile = self.ids[f"player{player}crape"].pile
            stock_label = self.ids[f"player{player}stockcount"]
            crape_label = self.ids[f"player{player}crapecount"]
            stock_label.text = str(len(stock_pile)) if stock_pile else ""
            crape_label.text = str(len(crape_pile)) if crape_pile else ""

    def move_card(
        self,
        card_widget: CardWidget,
        pile_widget: PileWidget,
        duration=DEFAULT_MOVE_DURATION,
    ):
        """Low level card move."""
        self.put_on_top(card_widget)

        # Remove from previous pile
        card_widget.pile_widget.pop_card()

        # Add to new pile
        pile_widget.add_card_widget(card_widget)
        card_widget.animate_move_to_pile(duration)

        self.update_counts()

    def set_active_player(self, player: int):
        """Change the active player and updates the GUI accordingly."""
        next_player_btn = self.ids[f"player{player}crapebutton"]
        next_player_btn.disabled = False
        Animation(
            opacity=1, duration=TRANSITION_DURATION, transition="out_cubic"
        ).start(next_player_btn)

        prev_player_btn = self.ids[f"player{1 - player}crapebutton"]
        prev_player_btn.disabled = True
        Animation(
            opacity=0, duration=TRANSITION_DURATION, transition="out_cubic"
        ).start(prev_player_btn)

        self.place_background_halo(player)

    def place_background_halo(self, player):
        """Place the background ahlo indicating that it's the player's turn."""
        background_halo = self.ids["background_halo"]
        Animation(
            y=0 if player == 0 else self.app.root.height,
            duration=TRANSITION_DURATION,
            transition="in_out_expo",
        ).start(background_halo)

    def flip_card_up(self, card_widget: CardWidget, duration=DEFAULT_FLIP_DURATION):
        """Flips up the card widget."""
        card_widget.set_face_up(duration)

    def flip_pile(self, pile_widget: PileWidget):
        # Update cards
        for card in pile_widget.pile:
            card.face_up = not card.face_up
            card_widget = self.card_widgets[card]
            card_widget.update_image()
            self.put_on_top(card_widget)

    def flip_waste_to_stock(self, player: int):
        """When the stock is empty, flip the waste back to the stock."""
        stock_widget = self.ids[f"player{player}stock"]
        waste_widget = self.ids[f"player{player}waste"]

        # Update model
        stock_widget.pile.set_cards(waste_widget.pile[::-1])
        waste_widget.pile.clear()

        # Update cards
        for card in stock_widget.pile:
            card.face_up = False
            card_widget = self.card_widgets[card]
            card_widget.update_image()
            card_widget.pile_widget = stock_widget
            card_widget.animate_move_to_pile()
            self.put_on_top(card_widget)
        self.update_counts()

    def put_on_top(self, card_widget: CardWidget):
        """Put a card widget above the other cards on the board widget."""
        self.app.root.remove_widget(card_widget)
        self.app.root.add_widget(card_widget)

    def set_crapette_mode(self, crapette_mode, player: int):
        """Toggle the crapette mode."""
        ids = self.app.root.ids
        crapette_button = ids[f"player{player}crapebutton"]

        background_crapette = self.ids["background_crapette"]
        background_crapette.opacity = 1 if crapette_mode else 0
        crapette_button.text = "Cancel ! (Sorry...)" if crapette_mode else "Crapette !"