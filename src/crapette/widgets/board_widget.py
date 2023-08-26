import typing

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout

from crapette.core.piles import Pile

from .card_widget import DEFAULT_FLIP_DURATION, DEFAULT_MOVE_DURATION, CardWidget
from .pile_widgets import PileWidget

if typing.TYPE_CHECKING:
    from crapette import game_manager
    from crapette.core.cards import Card

TRANSITION_DURATION = 0.5


class BoardWidget(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pile_widgets: list[PileWidget] = []
        self.card_widgets: dict[Card, CardWidget] = {}

        self.game_config = None
        self._do_layout_event = None
        self._piles_widgets_name_cache = {}
        self.stock_widgets = []
        self.crape_widgets = []
        self.waste_widgets = []

    def do_layout(self, *args, **kwargs):
        """Delay the layout computing to avoid visual lag."""
        if self._do_layout_event is not None:
            self._do_layout_event.cancel()

        super_do_layout = super().do_layout

        def real_do_layout(_dt):
            super_do_layout(*args, **kwargs)

            self.place_cards()
            if self.game_config:
                # with contextlib.suppress(KeyError):  # KeyError on window initialization
                self.place_background_halo()

        layout_delay_s = 0.2  # s
        self._do_layout_event = Clock.schedule_once(real_do_layout, layout_delay_s)

    def setup(self, game_manager: "game_manager.GameManager"):
        """Prepare and initialize the board for a new game."""
        self.app = App.get_running_app()
        self.ids = self.app.root.ids
        self.game_manager = game_manager
        self.game_config = game_manager.game_config

        self.board = self.game_config.board
        self.setup_piles()
        self.setup_card_widgets()
        self.place_cards()
        self.update_counts()
        self.init_keyboard()

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
        self.stock_widgets = [self.ids["player0stock"], self.ids["player1stock"]]
        self.crape_widgets = [self.ids["player0crape"], self.ids["player1crape"]]
        self.waste_widgets = [self.ids["player0waste"], self.ids["player1waste"]]
        for tableau, tableau_pile in enumerate(self.board.tableau_piles):
            self.pile_widgets.append(self.ids[f"tableau{tableau}"])
            self.ids[f"tableau{tableau}"].set_pile(tableau_pile)
        for foundation, foundation_pile in enumerate(self.board.foundation_piles):
            self.pile_widgets.append(self.ids[f"foundation{foundation}"])
            self.ids[f"foundation{foundation}"].set_pile(foundation_pile)
        self._piles_widgets_name_cache = {p.pile.name: p for p in self.pile_widgets}

    def widget_from_pile(self, pile: Pile):
        return self._piles_widgets_name_cache[pile.name]

    def setup_card_widgets(self):
        """Create and add a widget for every card.

        Updates the `card_widgets` list.

        The cards are not placed on the board, see `place_cards`.
        """
        cards_layer = self.ids["cards_layer"]
        # Remove previous card widgets
        if self.card_widgets:
            for card_widget in self.card_widgets.values():
                cards_layer.remove_widget(card_widget)

        # Add all card widgets
        self.card_widgets = {}
        for pile_widget in self.pile_widgets:
            for card in pile_widget.pile:
                card_widget = CardWidget(card, self.game_manager)
                card_widget.pile_widget = pile_widget
                self.card_widgets[card] = card_widget
                cards_layer.add_widget(card_widget)

    def init_keyboard(self):
        self._keyboard = Window.request_keyboard(
            callback=self._keyboard_closed,
            target=self,
            input_type="text",
            keyboard_suggestions=False,
        )
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def place_cards(self):
        """Reset the card widget positions in the piles."""
        for pile_widget in self.pile_widgets:
            for index, card in enumerate(pile_widget.pile):
                card_widget = self.card_widgets[card]
                card_widget.center = pile_widget.card_pos(index)

    def update_counts(self):
        """Update displayed card counts."""
        for player in range(self.board.NB_PLAYERS):
            nb_stock = len(self.stock_widgets[player].pile)
            nb_waste = len(self.waste_widgets[player].pile)
            stock_label = self.ids[f"player{player}stockcount"]
            stock_label.text = f"{nb_stock}+{nb_waste}" if nb_stock or nb_waste else ""

            crape_pile = self.crape_widgets[player].pile
            crape_label = self.ids[f"player{player}crapecount"]
            if crape_pile:
                cards_up = len([c for c in crape_pile if c.face_up])
                cards_down = len(crape_pile) - cards_up
                crape_label.text = (
                    f"{cards_down}+{cards_up}" if cards_up else str(cards_down)
                )
            else:
                crape_label.text = ""

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

    def set_active_player(self):
        """Change the active player and updates the GUI accordingly."""
        if not self.game_config.is_opponent_ai:
            player = self.game_config.active_player

            next_player_btn = self.ids[f"player{player}crapebutton"]
            next_player_btn.disabled = True
            Animation(
                opacity=1, duration=TRANSITION_DURATION, transition="out_cubic"
            ).start(next_player_btn)

            prev_player_btn = self.ids[f"player{1 - player}crapebutton"]
            prev_player_btn.disabled = True
            Animation(
                opacity=0, duration=TRANSITION_DURATION, transition="out_cubic"
            ).start(prev_player_btn)

        self.place_background_halo()

    def update_crapette_button_status(self):
        crape_btn = self.ids[f"player{self.game_config.active_player}crapebutton"]
        crape_btn.disabled = (
            not self.game_config.crapette_mode and not self.game_config.last_move
        )

    def place_background_halo(self):
        """Place the background halo indicating that it's the player's turn."""
        background_halo = self.ids["background_halo"]
        Animation(
            y=0 if self.game_config.active_player == 0 else self.app.root.height,
            duration=TRANSITION_DURATION,
            transition="in_out_expo",
        ).start(background_halo)

    def flip_card_up(self, card_widget: CardWidget, duration=DEFAULT_FLIP_DURATION):
        """Flips up the card widget."""
        card_widget.set_face_up(duration)
        self.update_counts()

    def flip_pile(self, pile_widget: PileWidget):
        # Update cards
        for card in pile_widget.pile:
            card.face_up = not card.face_up
            card_widget = self.card_widgets[card]
            card_widget.update_image()
            self.put_on_top(card_widget)
        self.update_counts()

    def flip_waste_to_stock(self):
        """When the stock is empty, flip the waste back to the stock."""
        player = self.game_config.active_player
        stock_widget = self.stock_widgets[player]
        waste_widget = self.waste_widgets[player]

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
        cards_layer = self.ids["cards_layer"]
        cards_layer.remove_widget(card_widget)
        cards_layer.add_widget(card_widget)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Keycode is composed of an integer + a string
        if keycode[1] == "spacebar":
            # Return True to accept the key. Otherwise, it will be used by
            # the system.
            self.game_manager.toggle_crapette_mode()
            return True
        # TODO: on game end: keyboard.release()
        return False

    def update_crapette_mode(self):
        """Toggle the crapette mode."""
        crapette_button = self.ids[f"player{self.game_config.active_player}crapebutton"]

        background_crapette = self.ids["background_crapette"]
        if self.game_config.crapette_mode:
            background_crapette.opacity = 1
            crapette_button.text = "Cancel ! (Sorry...)"
        else:
            background_crapette.opacity = 0
            crapette_button.text = "Crapette !"
