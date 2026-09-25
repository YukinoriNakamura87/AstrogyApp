from unittest import TestCase

from lilly_scoring import ChartInput, PlanetInput, PlanetName as P, score_chart


def planet(name, longitude, house=1, retrograde=False, speed=1.0):
    return PlanetInput(name, longitude, house, retrograde, speed)


def chart(*planets, **overrides):
    defaults = {
        "house_cusps": {number: (number - 1) * 30 for number in range(1, 13)},
        "north_node_longitude": 200,
        "south_node_longitude": 20,
        "fixed_stars": {"Regulus": 150, "Spica": 204, "Algol": 56},
    }
    defaults.update(overrides)
    return ChartInput(tuple(planets), **defaults)


def complete(overrides=None, **chart_overrides):
    values = {
        P.SUN: (10, 7, False, .99), P.MOON: (40, 8, False, 13.2),
        P.MERCURY: (70, 9, False, 1.1), P.VENUS: (100, 10, False, 1.0),
        P.MARS: (130, 11, False, .6), P.JUPITER: (160, 12, False, .09),
        P.SATURN: (190, 1, False, .04),
    }
    values.update(overrides or {})
    return chart(*(planet(name, *data) for name, data in values.items()), **chart_overrides)


class LillyScoringTests(TestCase):
    def test_requires_all_seven_classical_planets(self):
        with self.assertRaisesRegex(ValueError, "Missing classical planets"):
            score_chart(chart(planet(P.SUN, 10)))

    def test_essential_boundary_and_peregrine_rules(self):
        result = score_chart(complete({P.JUPITER: (6, 7, False, .09), P.SUN: (100, 4, False, .99)}))
        jupiter = next(item for item in result.planets if item.planet == P.JUPITER)
        codes = {item.code for item in jupiter.essential.items}
        self.assertEqual(result.sect, "night")
        self.assertNotIn("term", codes)  # Aries 6° starts Venus' term.
        self.assertIn("triplicity", codes)
        self.assertNotIn("peregrine", codes)

    def test_detriment_does_not_prevent_peregrine(self):
        result = score_chart(complete({P.JUPITER: (75, 7, False, .09)}))
        jupiter = next(item for item in result.planets if item.planet == P.JUPITER)
        self.assertTrue({"detriment", "peregrine"}.issubset({item.code for item in jupiter.essential.items}))

    def test_mutual_reception_records_partner_and_type(self):
        result = score_chart(complete({P.SUN: (5, 7, False, .99), P.MARS: (125, 11, False, .6)}))
        sun = next(item for item in result.planets if item.planet == P.SUN)
        reception = next(item for item in sun.essential.items if item.code == "mutual_reception_domicile")
        self.assertEqual(reception.points, 5)
        self.assertEqual(reception.related_body, "Mars")

    def test_five_degree_rule_uses_next_house_score(self):
        result = score_chart(complete({P.SUN: (28, 1, False, .99)}))
        sun = next(item for item in result.planets if item.planet == P.SUN)
        house = next(item for item in sun.accidental.items if item.code == "house")
        self.assertEqual((house.label, house.points), ("第2ハウス", 3))
        self.assertIn("5度前ルール", house.description)

    def test_solar_condition_uses_priority_and_same_sign(self):
        result = score_chart(complete({P.SUN: (30.1, 7, False, .99), P.MERCURY: (29.9, 9, False, 1.1)}))
        mercury = next(item for item in result.planets if item.planet == P.MERCURY)
        codes = {item.code for item in mercury.accidental.items}
        self.assertIn("cazimi", codes)
        self.assertNotIn("combust", codes)

    def test_under_sunbeams_explains_cross_sign_combust_rejection(self):
        result = score_chart(complete({
            P.SUN: (29.9, 8, False, .99),
            P.MOON: (30.75, 8, False, 13.2),
        }))
        moon = next(item for item in result.planets if item.planet == P.MOON)
        solar_condition = next(
            item for item in moon.accidental.items if item.code == "under_sunbeams"
        )
        self.assertEqual(solar_condition.points, -4)
        self.assertIn("太陽とはサイン違いのためコンバスト不成立", solar_condition.description)

    def test_oriental_occidental_is_omitted_within_one_degree(self):
        result = score_chart(complete({P.SUN: (30, 7, False, .99), P.MERCURY: (29, 9, False, 1.1)}))
        mercury = next(item for item in result.planets if item.planet == P.MERCURY)
        codes = {item.code for item in mercury.accidental.items}
        self.assertNotIn("oriental", codes)
        self.assertNotIn("occidental", codes)

    def test_exact_opposition_prefers_oriental(self):
        result = score_chart(complete({P.SUN: (200, 7, False, .99), P.JUPITER: (20, 12, False, .09)}))
        jupiter = next(item for item in result.planets if item.planet == P.JUPITER)
        orientation = next(item for item in jupiter.accidental.items if item.code == "oriental")
        self.assertEqual(orientation.points, 2)

    def test_client_8_moon_and_mercury_orientation_regression(self):
        result = score_chart(complete({
            P.SUN: (44.39583650352319, 2, False, .96903120742239),
            P.MOON: (86.39413694835895, 4, False, 13.188228026107497),
            P.MERCURY: (26.332820105209066, 2, True, -.07002037014225794),
        }))
        moon = next(item for item in result.planets if item.planet == P.MOON)
        mercury = next(item for item in result.planets if item.planet == P.MERCURY)
        moon_orientation = next(item for item in moon.accidental.items if item.code == "occidental")
        mercury_orientation = next(item for item in mercury.accidental.items if item.code == "oriental")
        self.assertEqual(moon_orientation.points, 2)
        self.assertIn("41°59′", moon_orientation.description)
        self.assertEqual(mercury_orientation.points, -2)
        self.assertIn("341°56′", mercury_orientation.description)

    def test_score_descriptions_do_not_use_decimal_degrees(self):
        result = score_chart(complete({
            P.SUN: (29.9, 8, False, .985556),
            P.MOON: (30.748204791, 8, False, 13.743411),
        }))
        descriptions = [
            item.description
            for planet_score in result.planets
            for section in (planet_score.essential, planet_score.accidental)
            for item in section.items
        ]
        self.assertTrue(any("0°50′" in description for description in descriptions))
        for description in descriptions:
            self.assertNotRegex(description, r"\d+\.\d+°")

    def test_daily_motion_uses_degree_minute_second_format(self):
        result = score_chart(complete({P.SATURN: (190, 1, False, .04)}))
        saturn = next(item for item in result.planets if item.planet == P.SATURN)
        speed = next(item for item in saturn.accidental.items if item.code == "fast")
        self.assertEqual(speed.description, "日運動 0°02′24″ > 平均 0°02′01″")

    def test_missing_fixed_stars_are_explicitly_unavailable(self):
        result = score_chart(complete(fixed_stars={}))
        self.assertTrue(result.warnings)
        for scored in result.planets:
            unavailable = next(item for item in scored.accidental.items if item.code == "fixed_stars_unavailable")
            self.assertEqual((unavailable.points, unavailable.status), (0, "unavailable"))

    def test_domicile_and_exaltation_can_both_score(self):
        result = score_chart(complete({P.MERCURY: (165, 9, False, 1.1)}))
        mercury = next(item for item in result.planets if item.planet == P.MERCURY)
        codes = {item.code for item in mercury.essential.items}
        self.assertTrue({"domicile", "exaltation"}.issubset(codes))

    def test_partile_aspects_and_node_conjunction_stack(self):
        result = score_chart(complete({
            P.MERCURY: (10, 9, False, 1.1),
            P.VENUS: (70.5, 10, False, 1.0),
            P.MARS: (100.5, 11, False, .6),
        }, north_node_longitude=10.8))
        mercury = next(item for item in result.planets if item.planet == P.MERCURY)
        codes = {item.code for item in mercury.accidental.items}
        self.assertTrue({"north_node_conjunction", "benefic_60", "malefic_90"}.issubset(codes))

    def test_besieged_handles_zero_degree_wrap(self):
        result = score_chart(complete({
            P.MOON: (1, 8, False, 13.2),
            P.MARS: (359, 11, False, .6),
            P.SATURN: (3, 1, False, .04),
        }))
        moon = next(item for item in result.planets if item.planet == P.MOON)
        self.assertIn("besieged", {item.code for item in moon.accidental.items})

    def test_fixed_star_orbs_are_scored(self):
        result = score_chart(complete({P.SUN: (150.5, 7, False, .99)}))
        sun = next(item for item in result.planets if item.planet == P.SUN)
        star = next(item for item in sun.accidental.items if item.code == "fixed_star_regulus")
        self.assertEqual(star.points, 6)
