"""Tests for battle turn order, targeting, and termination."""

import unittest

from combat.battle import Battle, BattleOutcome, create_default_battle
from combat.combat import InvalidActionError
from combat.models import Character, Team


def _make_battle(
    player_stats=((30, 10), (25, 12), (35, 8)),
    enemy_stats=((25, 7), (25, 7)),
) -> Battle:
    players = [
        Character(f"Player {i + 1}", hp=hp, attack=atk, team=Team.PLAYER)
        for i, (hp, atk) in enumerate(player_stats)
    ]
    enemies = [
        Character(f"Enemy {i + 1}", hp=hp, attack=atk, team=Team.ENEMY)
        for i, (hp, atk) in enumerate(enemy_stats)
    ]
    return Battle(players, enemies)


class DefaultBattleTests(unittest.TestCase):
    def test_default_starting_statistics(self) -> None:
        battle = create_default_battle()
        self.assertEqual(
            [(c.name, c.hp, c.attack) for c in battle.players],
            [("Player 1", 30, 10), ("Player 2", 25, 12), ("Player 3", 35, 8)],
        )
        self.assertEqual(
            [(c.name, c.hp, c.attack) for c in battle.enemies],
            [("Enemy 1", 25, 7), ("Enemy 2", 25, 7)],
        )
        self.assertEqual(battle.outcome, BattleOutcome.ONGOING)
        self.assertEqual(battle.round_number, 1)
        self.assertIs(battle.current_actor(), battle.players[0])


class BattleConstructionTests(unittest.TestCase):
    def test_duplicate_names_are_allowed(self) -> None:
        players = [
            Character("Fighter", hp=30, attack=10, team=Team.PLAYER),
            Character("Fighter", hp=25, attack=12, team=Team.PLAYER),
            Character("Support", hp=35, attack=8, team=Team.PLAYER),
        ]
        enemies = [
            Character("Fighter", hp=25, attack=7, team=Team.ENEMY),
            Character("Brute", hp=25, attack=7, team=Team.ENEMY),
        ]
        battle = Battle(players, enemies)
        self.assertIs(battle.current_actor(), battle.players[0])
        self.assertEqual(battle.players[0].name, battle.players[1].name)

    def test_wrong_player_count_rejected(self) -> None:
        players = [
            Character("Player 1", hp=30, attack=10, team=Team.PLAYER),
            Character("Player 2", hp=25, attack=12, team=Team.PLAYER),
        ]
        enemies = [
            Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY),
            Character("Enemy 2", hp=25, attack=7, team=Team.ENEMY),
        ]
        with self.assertRaises(ValueError):
            Battle(players, enemies)

    def test_wrong_enemy_count_rejected(self) -> None:
        players = [
            Character("Player 1", hp=30, attack=10, team=Team.PLAYER),
            Character("Player 2", hp=25, attack=12, team=Team.PLAYER),
            Character("Player 3", hp=35, attack=8, team=Team.PLAYER),
        ]
        enemies = [
            Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY),
        ]
        with self.assertRaises(ValueError):
            Battle(players, enemies)

    def test_player_with_enemy_team_rejected(self) -> None:
        players = [
            Character("Player 1", hp=30, attack=10, team=Team.PLAYER),
            Character("Player 2", hp=25, attack=12, team=Team.ENEMY),
            Character("Player 3", hp=35, attack=8, team=Team.PLAYER),
        ]
        enemies = [
            Character("Enemy 1", hp=25, attack=7, team=Team.ENEMY),
            Character("Enemy 2", hp=25, attack=7, team=Team.ENEMY),
        ]
        with self.assertRaises(ValueError):
            Battle(players, enemies)

    def test_enemy_with_player_team_rejected(self) -> None:
        players = [
            Character("Player 1", hp=30, attack=10, team=Team.PLAYER),
            Character("Player 2", hp=25, attack=12, team=Team.PLAYER),
            Character("Player 3", hp=35, attack=8, team=Team.PLAYER),
        ]
        enemies = [
            Character("Enemy 1", hp=25, attack=7, team=Team.PLAYER),
            Character("Enemy 2", hp=25, attack=7, team=Team.ENEMY),
        ]
        with self.assertRaises(ValueError):
            Battle(players, enemies)


class TurnOrderTests(unittest.TestCase):
    def test_fixed_turn_order_across_round(self) -> None:
        battle = _make_battle()
        expected = battle.players + battle.enemies
        # Spread player damage across both enemies so neither is defeated
        # before their turns (default stats: 10+12+8 would KO Enemy 1 alone).
        player_targets = [
            battle.enemies[0],
            battle.enemies[1],
            battle.enemies[0],
        ]
        player_target_index = 0
        for actor in expected:
            self.assertIs(battle.current_actor(), actor)
            if actor.team == Team.PLAYER:
                target = player_targets[player_target_index]
                player_target_index += 1
            else:
                target = battle.players[0]
            battle.attack(actor, target)

        self.assertEqual(battle.round_number, 2)
        self.assertIs(battle.current_actor(), battle.players[0])

    def test_defeated_characters_skip_their_turns(self) -> None:
        # Player 2 starts defeated and must be skipped.
        battle = _make_battle(
            player_stats=((30, 10), (0, 12), (35, 8)),
            enemy_stats=((25, 7), (25, 7)),
        )
        self.assertIs(battle.current_actor(), battle.players[0])
        battle.attack(battle.players[0], battle.enemies[0])
        # Player 2 is skipped; next actor is Player 3.
        self.assertIs(battle.current_actor(), battle.players[2])

    def test_initial_turn_skips_consecutive_defeated_players(self) -> None:
        # Players 1 and 2 start defeated; init must skip both to Player 3.
        battle = _make_battle(player_stats=((0, 10), (0, 12), (35, 8)))
        self.assertIs(battle.current_actor(), battle.players[2])
        self.assertEqual(battle.round_number, 1)
        self.assertEqual(battle.outcome, BattleOutcome.ONGOING)
        self.assertFalse(battle.is_over)

        battle.attack(battle.players[2], battle.enemies[0])
        self.assertEqual(battle.enemies[0].hp, 17)
        self.assertIs(battle.current_actor(), battle.enemies[0])
        self.assertEqual(battle.round_number, 1)
        self.assertEqual(battle.outcome, BattleOutcome.ONGOING)
        self.assertEqual(battle.players[0].hp, 0)
        self.assertEqual(battle.players[1].hp, 0)

    def test_enemy_defeated_before_turn_is_skipped(self) -> None:
        # Players focus Enemy 1 so it dies before its turn.
        battle = _make_battle(
            player_stats=((30, 10), (25, 12), (35, 8)),
            enemy_stats=((25, 7), (25, 7)),
        )
        battle.attack(battle.players[0], battle.enemies[0])
        battle.attack(battle.players[1], battle.enemies[0])
        battle.attack(battle.players[2], battle.enemies[0])
        self.assertFalse(battle.enemies[0].is_alive)
        self.assertIs(battle.current_actor(), battle.enemies[1])

    def test_round_advances_when_last_enemy_is_defeated_before_turn(self) -> None:
        # Enemy 2 is last in turn order. Defeat it during player turns while
        # Enemy 1 remains alive so the battle continues into the next round.
        battle = _make_battle(
            player_stats=((30, 10), (25, 12), (35, 8)),
            enemy_stats=((40, 7), (25, 7)),
        )
        battle.attack(battle.players[0], battle.enemies[1])
        battle.attack(battle.players[1], battle.enemies[1])
        battle.attack(battle.players[2], battle.enemies[1])
        self.assertFalse(battle.enemies[1].is_alive)
        self.assertTrue(battle.enemies[0].is_alive)

        self.assertIs(battle.current_actor(), battle.enemies[0])
        battle.attack(battle.enemies[0], battle.players[0])

        self.assertEqual(battle.round_number, 2)
        self.assertIs(battle.current_actor(), battle.players[0])

    def test_surviving_actors_act_again_next_round(self) -> None:
        battle = _make_battle()
        battle.attack(battle.players[0], battle.enemies[0])
        battle.attack(battle.players[1], battle.enemies[1])
        battle.attack(battle.players[2], battle.enemies[0])
        battle.attack(battle.enemies[0], battle.players[0])
        battle.attack(battle.enemies[1], battle.players[1])

        self.assertEqual(battle.round_number, 2)
        self.assertIs(battle.current_actor(), battle.players[0])
        self.assertTrue(battle.players[0].is_alive)

        # Enemy 2 still has enough HP for a full attack without flooring.
        hp_before = battle.enemies[1].hp
        battle.attack(battle.players[0], battle.enemies[1])
        self.assertEqual(battle.enemies[1].hp, hp_before - battle.players[0].attack)
        self.assertIs(battle.current_actor(), battle.players[1])

    def test_out_of_turn_attack_rejected_without_state_change(self) -> None:
        battle = _make_battle()
        enemy_hp = battle.enemies[0].hp
        with self.assertRaises(InvalidActionError):
            battle.attack(battle.players[1], battle.enemies[0])
        self.assertEqual(battle.enemies[0].hp, enemy_hp)
        self.assertIs(battle.current_actor(), battle.players[0])
        self.assertEqual(battle.round_number, 1)

    def test_character_cannot_attack_twice_in_same_round(self) -> None:
        battle = _make_battle()
        battle.attack(battle.players[0], battle.enemies[0])
        # Turn has advanced; Player 1 acting again is invalid.
        with self.assertRaises(InvalidActionError):
            battle.attack(battle.players[0], battle.enemies[0])
        self.assertIs(battle.current_actor(), battle.players[1])


class TargetingTests(unittest.TestCase):
    def test_cannot_target_ally(self) -> None:
        battle = _make_battle()
        ally_hp = battle.players[1].hp
        with self.assertRaises(InvalidActionError):
            battle.attack(battle.players[0], battle.players[1])
        self.assertEqual(battle.players[1].hp, ally_hp)
        self.assertIs(battle.current_actor(), battle.players[0])

    def test_cannot_target_defeated_enemy(self) -> None:
        battle = _make_battle(enemy_stats=((0, 7), (25, 7)))
        remaining_hp = battle.enemies[1].hp
        with self.assertRaises(InvalidActionError):
            battle.attack(battle.players[0], battle.enemies[0])
        self.assertEqual(battle.enemies[1].hp, remaining_hp)
        self.assertFalse(battle.enemies[0].is_alive)
        self.assertIs(battle.current_actor(), battle.players[0])

    def test_cannot_target_outsider(self) -> None:
        battle = _make_battle()
        outsider = Character("Outsider", hp=50, attack=1, team=Team.ENEMY)
        with self.assertRaises(InvalidActionError):
            battle.attack(battle.players[0], outsider)
        self.assertIs(battle.current_actor(), battle.players[0])

    def test_invalid_action_leaves_full_battle_state_unchanged(self) -> None:
        battle = _make_battle()
        snapshot = (
            battle.round_number,
            battle.outcome,
            battle.current_actor(),
            [c.hp for c in battle.players],
            [c.hp for c in battle.enemies],
        )
        with self.assertRaises(InvalidActionError):
            battle.attack(battle.players[0], battle.players[1])
        self.assertEqual(
            (
                battle.round_number,
                battle.outcome,
                battle.current_actor(),
                [c.hp for c in battle.players],
                [c.hp for c in battle.enemies],
            ),
            snapshot,
        )

    def test_enemy_must_also_specify_valid_target(self) -> None:
        battle = _make_battle()
        # Spread damage so Enemy 1 survives and remains the next actor.
        battle.attack(battle.players[0], battle.enemies[0])
        battle.attack(battle.players[1], battle.enemies[1])
        battle.attack(battle.players[2], battle.enemies[0])
        self.assertIs(battle.current_actor(), battle.enemies[0])

        with self.assertRaises(InvalidActionError):
            battle.attack(battle.enemies[0], battle.enemies[1])
        self.assertIs(battle.current_actor(), battle.enemies[0])

        battle.attack(battle.enemies[0], battle.players[0])
        self.assertEqual(battle.players[0].hp, 23)


class BattleTerminationTests(unittest.TestCase):
    def test_victory_when_all_enemies_defeated(self) -> None:
        # High player damage so two attacks can clear both enemies.
        battle = _make_battle(
            player_stats=((30, 25), (25, 25), (35, 8)),
            enemy_stats=((25, 7), (25, 7)),
        )
        battle.attack(battle.players[0], battle.enemies[0])
        self.assertFalse(battle.enemies[0].is_alive)
        self.assertEqual(battle.outcome, BattleOutcome.ONGOING)

        battle.attack(battle.players[1], battle.enemies[1])
        self.assertFalse(battle.enemies[1].is_alive)
        self.assertEqual(battle.outcome, BattleOutcome.VICTORY)
        self.assertTrue(battle.is_over)
        self.assertIsNone(battle.current_actor())

    def test_defeat_when_all_players_defeated(self) -> None:
        # Enemies deal 7 damage; each player has 7 HP and deals 0 damage.
        battle = _make_battle(
            player_stats=((7, 0), (7, 0), (7, 0)),
            enemy_stats=((25, 7), (25, 7)),
        )
        battle.attack(battle.players[0], battle.enemies[0])
        battle.attack(battle.players[1], battle.enemies[0])
        battle.attack(battle.players[2], battle.enemies[0])
        battle.attack(battle.enemies[0], battle.players[0])
        battle.attack(battle.enemies[1], battle.players[1])

        self.assertEqual(battle.round_number, 2)
        self.assertFalse(battle.players[0].is_alive)
        self.assertFalse(battle.players[1].is_alive)
        self.assertTrue(battle.players[2].is_alive)
        # Defeated Player 1 and Player 2 are skipped.
        self.assertIs(battle.current_actor(), battle.players[2])

        battle.attack(battle.players[2], battle.enemies[0])
        self.assertIs(battle.current_actor(), battle.enemies[0])
        battle.attack(battle.enemies[0], battle.players[2])

        self.assertEqual(battle.outcome, BattleOutcome.DEFEAT)
        self.assertTrue(battle.is_over)
        self.assertIsNone(battle.current_actor())

    def test_combat_ends_immediately_no_further_actions(self) -> None:
        battle = _make_battle(
            player_stats=((30, 25), (25, 25), (35, 8)),
            enemy_stats=((25, 7), (25, 7)),
        )
        battle.attack(battle.players[0], battle.enemies[0])
        battle.attack(battle.players[1], battle.enemies[1])
        self.assertEqual(battle.outcome, BattleOutcome.VICTORY)

        with self.assertRaises(InvalidActionError):
            battle.attack(battle.players[2], battle.enemies[0])

    def test_actions_rejected_after_defeat(self) -> None:
        battle = _make_battle(
            player_stats=((7, 0), (0, 0), (0, 0)),
            enemy_stats=((25, 7), (25, 7)),
        )
        # Player 2 and Player 3 start defeated; only Player 1 acts, then Enemy 1.
        self.assertIs(battle.current_actor(), battle.players[0])
        battle.attack(battle.players[0], battle.enemies[0])
        self.assertIs(battle.current_actor(), battle.enemies[0])
        battle.attack(battle.enemies[0], battle.players[0])

        self.assertEqual(battle.outcome, BattleOutcome.DEFEAT)
        self.assertTrue(battle.is_over)
        with self.assertRaises(InvalidActionError):
            battle.attack(battle.enemies[1], battle.players[0])

    def test_damage_clamped_when_finishing_blow_exceeds_hp(self) -> None:
        battle = _make_battle(
            player_stats=((30, 10), (25, 12), (35, 8)),
            enemy_stats=((5, 7), (25, 7)),
        )
        battle.attack(battle.players[0], battle.enemies[0])
        self.assertEqual(battle.enemies[0].hp, 0)
        self.assertFalse(battle.enemies[0].is_alive)


class BattleSnapshotTests(unittest.TestCase):
    def test_snapshot_contains_expected_fields(self) -> None:
        battle = create_default_battle()
        data = battle.snapshot()

        self.assertEqual(data["round_number"], 1)
        self.assertEqual(data["outcome"], "ongoing")
        self.assertEqual(data["current_actor"], "Player 1")
        self.assertEqual(
            data["players"],
            [
                {"name": "Player 1", "hp": 30, "attack": 10, "alive": True},
                {"name": "Player 2", "hp": 25, "attack": 12, "alive": True},
                {"name": "Player 3", "hp": 35, "attack": 8, "alive": True},
            ],
        )
        self.assertEqual(
            data["enemies"],
            [
                {"name": "Enemy 1", "hp": 25, "attack": 7, "alive": True},
                {"name": "Enemy 2", "hp": 25, "attack": 7, "alive": True},
            ],
        )

    def test_snapshot_reflects_mid_battle_state(self) -> None:
        battle = _make_battle()
        battle.attack(battle.players[0], battle.enemies[0])
        data = battle.snapshot()

        self.assertEqual(data["round_number"], 1)
        self.assertEqual(data["outcome"], "ongoing")
        self.assertEqual(data["current_actor"], "Player 2")
        self.assertEqual(data["enemies"][0]["hp"], 15)
        self.assertTrue(data["enemies"][0]["alive"])

    def test_snapshot_current_actor_none_when_battle_over(self) -> None:
        battle = _make_battle(
            player_stats=((30, 25), (25, 25), (35, 8)),
            enemy_stats=((25, 7), (25, 7)),
        )
        battle.attack(battle.players[0], battle.enemies[0])
        battle.attack(battle.players[1], battle.enemies[1])

        data = battle.snapshot()
        self.assertEqual(data["outcome"], "victory")
        self.assertIsNone(data["current_actor"])
        self.assertFalse(data["enemies"][0]["alive"])
        self.assertFalse(data["enemies"][1]["alive"])

    def test_snapshot_does_not_modify_battle_state(self) -> None:
        battle = _make_battle()
        before = (
            battle.round_number,
            battle.outcome,
            battle.current_actor(),
            [c.hp for c in battle.players],
            [c.hp for c in battle.enemies],
        )
        battle.snapshot()
        after = (
            battle.round_number,
            battle.outcome,
            battle.current_actor(),
            [c.hp for c in battle.players],
            [c.hp for c in battle.enemies],
        )
        self.assertEqual(before, after)

    def test_snapshot_is_detached_from_live_characters(self) -> None:
        battle = _make_battle()
        data = battle.snapshot()

        data["players"][0]["hp"] = 1
        data["enemies"][0]["alive"] = False
        data["round_number"] = 99
        data["outcome"] = "defeat"
        data["current_actor"] = "Nobody"

        self.assertEqual(battle.players[0].hp, 30)
        self.assertTrue(battle.enemies[0].is_alive)
        self.assertEqual(battle.round_number, 1)
        self.assertEqual(battle.outcome, BattleOutcome.ONGOING)
        self.assertIs(battle.current_actor(), battle.players[0])


class DeterminismTests(unittest.TestCase):
    def test_same_actions_produce_same_result(self) -> None:
        def run() -> tuple:
            battle = create_default_battle()
            battle.attack(battle.players[0], battle.enemies[0])
            battle.attack(battle.players[1], battle.enemies[0])
            battle.attack(battle.players[2], battle.enemies[1])
            battle.attack(battle.enemies[0], battle.players[0])
            battle.attack(battle.enemies[1], battle.players[1])
            return (
                battle.round_number,
                [c.hp for c in battle.players],
                [c.hp for c in battle.enemies],
                battle.outcome,
            )

        self.assertEqual(run(), run())


if __name__ == "__main__":
    unittest.main()
