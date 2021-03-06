import logging
from typing import Callable

from PySide2.QtCore import QSize, Qt, QItemSelectionModel, QPoint
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import (
    QLabel,
    QDialog,
    QGridLayout,
    QListView,
    QStackedLayout,
    QComboBox,
    QWidget,
    QAbstractItemView,
    QPushButton,
    QGroupBox,
    QCheckBox,
    QVBoxLayout,
    QSpinBox,
)
from dcs.forcedoptions import ForcedOptions

import qt_ui.uiconstants as CONST
from game.game import Game
from game.infos.information import Information
from qt_ui.widgets.QLabeledWidget import QLabeledWidget
from qt_ui.windows.GameUpdateSignal import GameUpdateSignal
from qt_ui.windows.finances.QFinancesMenu import QHorizontalSeparationLine
from qt_ui.windows.settings.plugins import PluginOptionsPage, PluginsPage


class CheatSettingsBox(QGroupBox):
    def __init__(self, game: Game, apply_settings: Callable[[], None]) -> None:
        super().__init__("Cheat Settings")
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.red_ato_checkbox = QCheckBox()
        self.red_ato_checkbox.setChecked(game.settings.show_red_ato)
        self.red_ato_checkbox.toggled.connect(apply_settings)
        self.red_ato = QLabeledWidget("Show Red ATO:", self.red_ato_checkbox)
        self.main_layout.addLayout(self.red_ato)

    @property
    def show_red_ato(self) -> bool:
        return self.red_ato_checkbox.isChecked()


class QSettingsWindow(QDialog):

    def __init__(self, game: Game):
        super(QSettingsWindow, self).__init__()

        self.game = game
        self.pluginsPage = None
        self.pluginsOptionsPage = None

        self.setModal(True)
        self.setWindowTitle("Settings")
        self.setWindowIcon(CONST.ICONS["Settings"])
        self.setMinimumSize(600, 250)

        self.initUi()

    def initUi(self):
        self.layout = QGridLayout()

        self.categoryList = QListView()
        self.right_layout = QStackedLayout()

        self.categoryList.setMaximumWidth(175)

        self.categoryModel = QStandardItemModel(self.categoryList)

        self.categoryList.setIconSize(QSize(32, 32))

        self.initDifficultyLayout()
        difficulty = QStandardItem("Difficulty")
        difficulty.setIcon(CONST.ICONS["Missile"])
        difficulty.setEditable(False)
        difficulty.setSelectable(True)
        self.categoryModel.appendRow(difficulty)
        self.right_layout.addWidget(self.difficultyPage)

        self.initGeneratorLayout()
        generator = QStandardItem("Mission Generator")
        generator.setIcon(CONST.ICONS["Generator"])
        generator.setEditable(False)
        generator.setSelectable(True)
        self.categoryModel.appendRow(generator)
        self.right_layout.addWidget(self.generatorPage)

        self.initCheatLayout()
        cheat = QStandardItem("Cheat Menu")
        cheat.setIcon(CONST.ICONS["Cheat"])
        cheat.setEditable(False)
        cheat.setSelectable(True)
        self.categoryModel.appendRow(cheat)
        self.right_layout.addWidget(self.cheatPage)

        self.pluginsPage = PluginsPage()
        plugins = QStandardItem("LUA Plugins")
        plugins.setIcon(CONST.ICONS["Plugins"])
        plugins.setEditable(False)
        plugins.setSelectable(True)
        self.categoryModel.appendRow(plugins)
        self.right_layout.addWidget(self.pluginsPage)

        self.pluginsOptionsPage = PluginOptionsPage()
        pluginsOptions = QStandardItem("LUA Plugins Options")
        pluginsOptions.setIcon(CONST.ICONS["PluginsOptions"])
        pluginsOptions.setEditable(False)
        pluginsOptions.setSelectable(True)
        self.categoryModel.appendRow(pluginsOptions)
        self.right_layout.addWidget(self.pluginsOptionsPage)

        self.categoryList.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.categoryList.setModel(self.categoryModel)
        self.categoryList.selectionModel().setCurrentIndex(self.categoryList.indexAt(QPoint(1,1)), QItemSelectionModel.Select)
        self.categoryList.selectionModel().selectionChanged.connect(self.onSelectionChanged)


        self.layout.addWidget(self.categoryList, 0, 0, 1, 1)
        self.layout.addLayout(self.right_layout, 0, 1, 5, 1)

        self.setLayout(self.layout)

    def init(self):
        pass

    def initDifficultyLayout(self):

        self.difficultyPage = QWidget()
        self.difficultyLayout = QGridLayout()
        self.difficultyLayout.setAlignment(Qt.AlignTop)
        self.difficultyPage.setLayout(self.difficultyLayout)

        self.playerCoalitionSkill = QComboBox()
        self.enemyCoalitionSkill = QComboBox()
        self.enemyAASkill = QComboBox()
        for skill in CONST.SKILL_OPTIONS:
            self.playerCoalitionSkill.addItem(skill)
            self.enemyCoalitionSkill.addItem(skill)
            self.enemyAASkill.addItem(skill)

        self.playerCoalitionSkill.setCurrentIndex(CONST.SKILL_OPTIONS.index(self.game.settings.player_skill))
        self.enemyCoalitionSkill.setCurrentIndex(CONST.SKILL_OPTIONS.index(self.game.settings.enemy_skill))
        self.enemyAASkill.setCurrentIndex(CONST.SKILL_OPTIONS.index(self.game.settings.enemy_vehicle_skill))

        self.playerCoalitionSkill.currentIndexChanged.connect(self.applySettings)
        self.enemyCoalitionSkill.currentIndexChanged.connect(self.applySettings)
        self.enemyAASkill.currentIndexChanged.connect(self.applySettings)

        self.difficultyLayout.addWidget(QLabel("Player coalition skill"), 0, 0)
        self.difficultyLayout.addWidget(self.playerCoalitionSkill, 0, 1, Qt.AlignRight)
        self.difficultyLayout.addWidget(QLabel("Enemy skill"), 1, 0)
        self.difficultyLayout.addWidget(self.enemyCoalitionSkill, 1, 1, Qt.AlignRight)
        self.difficultyLayout.addWidget(QLabel("Enemy AA and vehicles skill"), 2, 0)
        self.difficultyLayout.addWidget(self.enemyAASkill, 2, 1, Qt.AlignRight)

        self.difficultyLabel = QComboBox()
        [self.difficultyLabel.addItem(t) for t in CONST.LABELS_OPTIONS]
        self.difficultyLabel.setCurrentIndex(CONST.LABELS_OPTIONS.index(self.game.settings.labels))
        self.difficultyLabel.currentIndexChanged.connect(self.applySettings)

        self.difficultyLayout.addWidget(QLabel("In Game Labels"), 3, 0)
        self.difficultyLayout.addWidget(self.difficultyLabel, 3, 1, Qt.AlignRight)

        self.noNightMission = QCheckBox()
        self.noNightMission.setChecked(self.game.settings.night_disabled)
        self.noNightMission.toggled.connect(self.applySettings)
        self.difficultyLayout.addWidget(QLabel("No night missions"), 4, 0)
        self.difficultyLayout.addWidget(self.noNightMission, 4, 1, Qt.AlignRight)

        self.mapVisibiitySelection = QComboBox()
        self.mapVisibiitySelection.addItem("All", ForcedOptions.Views.All)
        if self.game.settings.map_coalition_visibility == ForcedOptions.Views.All:
            self.mapVisibiitySelection.setCurrentIndex(0)
        self.mapVisibiitySelection.addItem("Fog of War", ForcedOptions.Views.Allies)
        if self.game.settings.map_coalition_visibility == ForcedOptions.Views.Allies:
            self.mapVisibiitySelection.setCurrentIndex(1)
        self.mapVisibiitySelection.addItem("Allies Only", ForcedOptions.Views.OnlyAllies)
        if self.game.settings.map_coalition_visibility == ForcedOptions.Views.OnlyAllies:
            self.mapVisibiitySelection.setCurrentIndex(2)
        self.mapVisibiitySelection.addItem("Own Aircraft Only", ForcedOptions.Views.MyAircraft)
        if self.game.settings.map_coalition_visibility == ForcedOptions.Views.MyAircraft:
            self.mapVisibiitySelection.setCurrentIndex(3)
        self.mapVisibiitySelection.addItem("Map Only", ForcedOptions.Views.OnlyMap)
        if self.game.settings.map_coalition_visibility == ForcedOptions.Views.OnlyMap:
            self.mapVisibiitySelection.setCurrentIndex(4)
        self.mapVisibiitySelection.currentIndexChanged.connect(self.applySettings)
        self.difficultyLayout.addWidget(QLabel("Map visibility options"), 5, 0)
        self.difficultyLayout.addWidget(self.mapVisibiitySelection, 5, 1, Qt.AlignRight)

        self.ext_views = QCheckBox()
        self.ext_views.setChecked(self.game.settings.external_views_allowed)
        self.ext_views.toggled.connect(self.applySettings)
        self.difficultyLayout.addWidget(QLabel("Allow external views"), 6, 0)
        self.difficultyLayout.addWidget(self.ext_views, 6, 1, Qt.AlignRight)


    def initGeneratorLayout(self):
        self.generatorPage = QWidget()
        self.generatorLayout = QVBoxLayout()
        self.generatorLayout.setAlignment(Qt.AlignTop)
        self.generatorPage.setLayout(self.generatorLayout)

        self.gameplay = QGroupBox("Gameplay")
        self.gameplayLayout = QGridLayout()
        self.gameplayLayout.setAlignment(Qt.AlignTop)
        self.gameplay.setLayout(self.gameplayLayout)

        self.supercarrier = QCheckBox()
        self.supercarrier.setChecked(self.game.settings.supercarrier)
        self.supercarrier.toggled.connect(self.applySettings)

        self.generate_marks = QCheckBox()
        self.generate_marks.setChecked(self.game.settings.generate_marks)
        self.generate_marks.toggled.connect(self.applySettings)

        self.never_delay_players = QCheckBox()
        self.never_delay_players.setChecked(
            self.game.settings.never_delay_player_flights)
        self.never_delay_players.toggled.connect(self.applySettings)
        self.never_delay_players.setToolTip(
            "When checked, player flights with a delayed start time will be "
            "spawned immediately. AI wingmen may begin startup immediately."
        )

        self.gameplayLayout.addWidget(QLabel("Use Supercarrier Module"), 0, 0)
        self.gameplayLayout.addWidget(self.supercarrier, 0, 1, Qt.AlignRight)
        self.gameplayLayout.addWidget(QLabel("Put Objective Markers on Map"), 1, 0)
        self.gameplayLayout.addWidget(self.generate_marks, 1, 1, Qt.AlignRight)
        self.gameplayLayout.addWidget(
            QLabel("Never delay player flights"), 2, 0)
        self.gameplayLayout.addWidget(self.never_delay_players, 2, 1,
                                      Qt.AlignRight)

        self.performance = QGroupBox("Performance")
        self.performanceLayout = QGridLayout()
        self.performanceLayout.setAlignment(Qt.AlignTop)
        self.performance.setLayout(self.performanceLayout)

        self.smoke = QCheckBox()
        self.smoke.setChecked(self.game.settings.perf_smoke_gen)
        self.smoke.toggled.connect(self.applySettings)

        self.red_alert = QCheckBox()
        self.red_alert.setChecked(self.game.settings.perf_red_alert_state)
        self.red_alert.toggled.connect(self.applySettings)

        self.arti = QCheckBox()
        self.arti.setChecked(self.game.settings.perf_artillery)
        self.arti.toggled.connect(self.applySettings)

        self.moving_units = QCheckBox()
        self.moving_units.setChecked(self.game.settings.perf_moving_units)
        self.moving_units.toggled.connect(self.applySettings)

        self.infantry = QCheckBox()
        self.infantry.setChecked(self.game.settings.perf_infantry)
        self.infantry.toggled.connect(self.applySettings)

        self.ai_parking_start = QCheckBox()
        self.ai_parking_start.setChecked(self.game.settings.perf_ai_parking_start)
        self.ai_parking_start.toggled.connect(self.applySettings)

        self.destroyed_units = QCheckBox()
        self.destroyed_units.setChecked(self.game.settings.perf_destroyed_units)
        self.destroyed_units.toggled.connect(self.applySettings)

        self.culling = QCheckBox()
        self.culling.setChecked(self.game.settings.perf_culling)
        self.culling.toggled.connect(self.applySettings)

        self.culling_distance = QSpinBox()
        self.culling_distance.setMinimum(50)
        self.culling_distance.setMaximum(10000)
        self.culling_distance.setValue(self.game.settings.perf_culling_distance)
        self.culling_distance.valueChanged.connect(self.applySettings)

        self.performanceLayout.addWidget(QLabel("Smoke visual effect on frontline"), 0, 0)
        self.performanceLayout.addWidget(self.smoke, 0, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(QLabel("SAM starts in RED alert mode"), 1, 0)
        self.performanceLayout.addWidget(self.red_alert, 1, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(QLabel("Artillery strikes"), 2, 0)
        self.performanceLayout.addWidget(self.arti, 2, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(QLabel("Moving ground units"), 3, 0)
        self.performanceLayout.addWidget(self.moving_units, 3, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(QLabel("Generate infantry squads along vehicles"), 4, 0)
        self.performanceLayout.addWidget(self.infantry, 4, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(QLabel("AI planes parking start (AI starts in flight if disabled)"), 5, 0)
        self.performanceLayout.addWidget(self.ai_parking_start, 5, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(QLabel("Include destroyed units carcass"), 6, 0)
        self.performanceLayout.addWidget(self.destroyed_units, 6, 1, alignment=Qt.AlignRight)

        self.performanceLayout.addWidget(QHorizontalSeparationLine(), 7, 0, 1, 2)
        self.performanceLayout.addWidget(QLabel("Culling of distant units enabled"), 8, 0)
        self.performanceLayout.addWidget(self.culling, 8, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(QLabel("Culling distance (km)"), 9, 0)
        self.performanceLayout.addWidget(self.culling_distance, 9, 1, alignment=Qt.AlignRight)

        self.generatorLayout.addWidget(self.gameplay)
        self.generatorLayout.addWidget(QLabel("Disabling settings below may improve performance, but will impact the overall quality of the experience."))
        self.generatorLayout.addWidget(self.performance)


    def initCheatLayout(self):

        self.cheatPage = QWidget()
        self.cheatLayout = QVBoxLayout()
        self.cheatPage.setLayout(self.cheatLayout)

        self.cheat_options = CheatSettingsBox(self.game, self.applySettings)
        self.cheatLayout.addWidget(self.cheat_options)

        self.moneyCheatBox = QGroupBox("Money Cheat")
        self.moneyCheatBox.setAlignment(Qt.AlignTop)
        self.moneyCheatBoxLayout = QGridLayout()
        self.moneyCheatBox.setLayout(self.moneyCheatBoxLayout)

        cheats_amounts = [25, 50, 100, 200, 500, 1000, -25, -50, -100, -200]
        for i, amount in enumerate(cheats_amounts):
            if amount > 0:
                btn = QPushButton("Cheat +" + str(amount) + "M")
                btn.setProperty("style", "btn-success")
            else:
                btn = QPushButton("Cheat " + str(amount) + "M")
                btn.setProperty("style", "btn-danger")
            btn.clicked.connect(self.cheatLambda(amount))
            self.moneyCheatBoxLayout.addWidget(btn, i/2, i%2)
        self.cheatLayout.addWidget(self.moneyCheatBox, stretch=1)

    def cheatLambda(self, amount):
        return lambda: self.cheatMoney(amount)

    def cheatMoney(self, amount):
        logging.info("CHEATING FOR AMOUNT : " + str(amount) + "M")
        self.game.budget += amount
        if amount > 0:
            self.game.informations.append(Information("CHEATER", "You are a cheater and you should feel bad", self.game.turn))
        else:
            self.game.informations.append(Information("CHEATER", "You are still a cheater !", self.game.turn))
        GameUpdateSignal.get_instance().updateGame(self.game)

    def applySettings(self):
        self.game.settings.player_skill = CONST.SKILL_OPTIONS[self.playerCoalitionSkill.currentIndex()]
        self.game.settings.enemy_skill = CONST.SKILL_OPTIONS[self.enemyCoalitionSkill.currentIndex()]
        self.game.settings.enemy_vehicle_skill = CONST.SKILL_OPTIONS[self.enemyAASkill.currentIndex()]
        self.game.settings.labels = CONST.LABELS_OPTIONS[self.difficultyLabel.currentIndex()]
        self.game.settings.night_disabled = self.noNightMission.isChecked()
        self.game.settings.map_coalition_visibility = self.mapVisibiitySelection.currentData()
        self.game.settings.external_views_allowed = self.ext_views.isChecked()
        self.game.settings.generate_marks = self.generate_marks.isChecked()
        self.game.settings.never_delay_player_flights = self.never_delay_players.isChecked()

        self.game.settings.supercarrier = self.supercarrier.isChecked()

        self.game.settings.perf_red_alert_state = self.red_alert.isChecked()
        self.game.settings.perf_smoke_gen = self.smoke.isChecked()
        self.game.settings.perf_artillery = self.arti.isChecked()
        self.game.settings.perf_moving_units = self.moving_units.isChecked()
        self.game.settings.perf_infantry = self.infantry.isChecked()
        self.game.settings.perf_ai_parking_start = self.ai_parking_start.isChecked()
        self.game.settings.perf_destroyed_units = self.destroyed_units.isChecked()

        self.game.settings.perf_culling = self.culling.isChecked()
        self.game.settings.perf_culling_distance = int(self.culling_distance.value())

        self.game.settings.show_red_ato = self.cheat_options.show_red_ato

        GameUpdateSignal.get_instance().updateGame(self.game)

    def onSelectionChanged(self):
        index = self.categoryList.selectionModel().currentIndex().row()
        self.right_layout.setCurrentIndex(index)