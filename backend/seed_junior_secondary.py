#!/usr/bin/env python3
"""
Seed Junior Secondary curriculum data (Grade 7, 8, 9) for key subjects:
- Mathematics
- Integrated Science  
- Social Studies
- Pre-Technical Studies

Based on KICD CBC Curriculum Designs for Junior Secondary.
Run with: python seed_junior_secondary.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
db_name = os.environ.get('DB_NAME', 'cbeplanner')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# ============================================================================
# MATHEMATICS - GRADE 7, 8, 9 (KICD CBC Curriculum)
# ============================================================================
MATHEMATICS_DATA = {
    "strands": [
        {
            "name": "Numbers",
            "substrands": [
                {
                    "name": "Whole Numbers",
                    "slos": [
                        {"name": "Read and write whole numbers up to hundreds of millions", "description": "By the end of the lesson, the learner should be able to read and write whole numbers up to hundreds of millions in symbols and words."},
                        {"name": "Identify place value and total value of digits", "description": "By the end of the lesson, the learner should be able to identify the place value and total value of digits in whole numbers."},
                        {"name": "Round off whole numbers to the nearest place value", "description": "By the end of the lesson, the learner should be able to round off whole numbers to specified place values."},
                        {"name": "Perform operations on whole numbers", "description": "By the end of the lesson, the learner should be able to add, subtract, multiply and divide whole numbers."},
                        {"name": "Solve real-life problems involving whole numbers", "description": "By the end of the lesson, the learner should be able to solve real-life problems involving whole numbers."}
                    ]
                },
                {
                    "name": "Factors and Multiples",
                    "slos": [
                        {"name": "Identify factors of whole numbers", "description": "By the end of the lesson, the learner should be able to identify factors of whole numbers."},
                        {"name": "Work out prime factorization of numbers", "description": "By the end of the lesson, the learner should be able to express numbers as products of prime factors."},
                        {"name": "Determine GCD of numbers", "description": "By the end of the lesson, the learner should be able to determine the Greatest Common Divisor (GCD) of given numbers."},
                        {"name": "Determine LCM of numbers", "description": "By the end of the lesson, the learner should be able to determine the Lowest Common Multiple (LCM) of given numbers."},
                        {"name": "Apply GCD and LCM to solve problems", "description": "By the end of the lesson, the learner should be able to apply GCD and LCM in solving real-life problems."}
                    ]
                },
                {
                    "name": "Integers",
                    "slos": [
                        {"name": "Identify positive and negative integers", "description": "By the end of the lesson, the learner should be able to identify positive and negative integers on a number line."},
                        {"name": "Order integers on a number line", "description": "By the end of the lesson, the learner should be able to order integers on a number line."},
                        {"name": "Add and subtract integers", "description": "By the end of the lesson, the learner should be able to add and subtract integers."},
                        {"name": "Multiply and divide integers", "description": "By the end of the lesson, the learner should be able to multiply and divide integers."},
                        {"name": "Solve real-life problems involving integers", "description": "By the end of the lesson, the learner should be able to solve real-life problems involving integers."}
                    ]
                },
                {
                    "name": "Fractions",
                    "slos": [
                        {"name": "Identify types of fractions", "description": "By the end of the lesson, the learner should be able to identify proper, improper and mixed fractions."},
                        {"name": "Convert between mixed numbers and improper fractions", "description": "By the end of the lesson, the learner should be able to convert mixed numbers to improper fractions and vice versa."},
                        {"name": "Compare and order fractions", "description": "By the end of the lesson, the learner should be able to compare and order fractions."},
                        {"name": "Perform operations on fractions", "description": "By the end of the lesson, the learner should be able to add, subtract, multiply and divide fractions."},
                        {"name": "Solve problems involving fractions", "description": "By the end of the lesson, the learner should be able to solve real-life problems involving fractions."}
                    ]
                },
                {
                    "name": "Decimals",
                    "slos": [
                        {"name": "Identify place value of decimals", "description": "By the end of the lesson, the learner should be able to identify the place value of digits in decimals."},
                        {"name": "Convert fractions to decimals and vice versa", "description": "By the end of the lesson, the learner should be able to convert fractions to decimals and decimals to fractions."},
                        {"name": "Perform operations on decimals", "description": "By the end of the lesson, the learner should be able to add, subtract, multiply and divide decimals."},
                        {"name": "Round off decimals", "description": "By the end of the lesson, the learner should be able to round off decimals to specified decimal places."},
                        {"name": "Solve real-life problems involving decimals", "description": "By the end of the lesson, the learner should be able to solve real-life problems involving decimals."}
                    ]
                },
                {
                    "name": "Percentages",
                    "slos": [
                        {"name": "Convert fractions and decimals to percentages", "description": "By the end of the lesson, the learner should be able to convert fractions and decimals to percentages."},
                        {"name": "Calculate percentage of quantities", "description": "By the end of the lesson, the learner should be able to calculate percentage of given quantities."},
                        {"name": "Calculate percentage increase and decrease", "description": "By the end of the lesson, the learner should be able to calculate percentage increase and decrease."},
                        {"name": "Apply percentages in real-life situations", "description": "By the end of the lesson, the learner should be able to apply percentages in profit, loss, and discount calculations."}
                    ]
                }
            ]
        },
        {
            "name": "Algebra",
            "substrands": [
                {
                    "name": "Algebraic Expressions",
                    "slos": [
                        {"name": "Identify algebraic terms and expressions", "description": "By the end of the lesson, the learner should be able to identify terms, coefficients, and constants in algebraic expressions."},
                        {"name": "Simplify algebraic expressions", "description": "By the end of the lesson, the learner should be able to simplify algebraic expressions by collecting like terms."},
                        {"name": "Evaluate algebraic expressions", "description": "By the end of the lesson, the learner should be able to evaluate algebraic expressions by substituting given values."},
                        {"name": "Factorize algebraic expressions", "description": "By the end of the lesson, the learner should be able to factorize simple algebraic expressions."},
                        {"name": "Expand algebraic expressions", "description": "By the end of the lesson, the learner should be able to expand algebraic expressions using distributive law."}
                    ]
                },
                {
                    "name": "Linear Equations",
                    "slos": [
                        {"name": "Form linear equations from word problems", "description": "By the end of the lesson, the learner should be able to form linear equations from word problems."},
                        {"name": "Solve linear equations in one unknown", "description": "By the end of the lesson, the learner should be able to solve linear equations in one unknown."},
                        {"name": "Solve linear equations with fractions", "description": "By the end of the lesson, the learner should be able to solve linear equations involving fractions."},
                        {"name": "Apply linear equations to real-life problems", "description": "By the end of the lesson, the learner should be able to apply linear equations to solve real-life problems."}
                    ]
                },
                {
                    "name": "Inequalities",
                    "slos": [
                        {"name": "Identify inequality symbols", "description": "By the end of the lesson, the learner should be able to identify and use inequality symbols correctly."},
                        {"name": "Solve linear inequalities", "description": "By the end of the lesson, the learner should be able to solve linear inequalities in one variable."},
                        {"name": "Represent solutions on a number line", "description": "By the end of the lesson, the learner should be able to represent solutions of inequalities on a number line."},
                        {"name": "Apply inequalities in real-life situations", "description": "By the end of the lesson, the learner should be able to apply inequalities in solving real-life problems."}
                    ]
                },
                {
                    "name": "Formulae and Substitution",
                    "slos": [
                        {"name": "Derive simple formulae from word statements", "description": "By the end of the lesson, the learner should be able to derive simple formulae from given word statements."},
                        {"name": "Substitute values in formulae", "description": "By the end of the lesson, the learner should be able to substitute numerical values in formulae."},
                        {"name": "Change the subject of a formula", "description": "By the end of the lesson, the learner should be able to change the subject of simple formulae."},
                        {"name": "Apply formulae to solve problems", "description": "By the end of the lesson, the learner should be able to apply formulae to solve real-life problems."}
                    ]
                }
            ]
        },
        {
            "name": "Geometry",
            "substrands": [
                {
                    "name": "Lines and Angles",
                    "slos": [
                        {"name": "Identify types of lines", "description": "By the end of the lesson, the learner should be able to identify parallel, perpendicular, and intersecting lines."},
                        {"name": "Identify types of angles", "description": "By the end of the lesson, the learner should be able to identify acute, right, obtuse, straight, reflex and complete angles."},
                        {"name": "Measure and draw angles", "description": "By the end of the lesson, the learner should be able to measure and draw angles using a protractor."},
                        {"name": "Calculate angles on a straight line", "description": "By the end of the lesson, the learner should be able to calculate angles on a straight line."},
                        {"name": "Calculate angles at a point", "description": "By the end of the lesson, the learner should be able to calculate angles at a point."}
                    ]
                },
                {
                    "name": "Polygons",
                    "slos": [
                        {"name": "Identify different polygons", "description": "By the end of the lesson, the learner should be able to identify triangles, quadrilaterals, pentagons, hexagons and other polygons."},
                        {"name": "Calculate interior angles of polygons", "description": "By the end of the lesson, the learner should be able to calculate interior angles of regular polygons."},
                        {"name": "Calculate exterior angles of polygons", "description": "By the end of the lesson, the learner should be able to calculate exterior angles of regular polygons."},
                        {"name": "Identify properties of quadrilaterals", "description": "By the end of the lesson, the learner should be able to identify properties of different quadrilaterals."},
                        {"name": "Construct regular polygons", "description": "By the end of the lesson, the learner should be able to construct regular polygons using appropriate instruments."}
                    ]
                },
                {
                    "name": "Circles",
                    "slos": [
                        {"name": "Identify parts of a circle", "description": "By the end of the lesson, the learner should be able to identify radius, diameter, chord, arc, sector and segment of a circle."},
                        {"name": "Calculate circumference of a circle", "description": "By the end of the lesson, the learner should be able to calculate the circumference of a circle."},
                        {"name": "Calculate area of a circle", "description": "By the end of the lesson, the learner should be able to calculate the area of a circle."},
                        {"name": "Solve problems involving circles", "description": "By the end of the lesson, the learner should be able to solve problems involving circumference and area of circles."}
                    ]
                },
                {
                    "name": "Constructions",
                    "slos": [
                        {"name": "Construct perpendicular lines", "description": "By the end of the lesson, the learner should be able to construct perpendicular lines using compass and ruler."},
                        {"name": "Bisect lines and angles", "description": "By the end of the lesson, the learner should be able to bisect lines and angles using compass and ruler."},
                        {"name": "Construct triangles", "description": "By the end of the lesson, the learner should be able to construct triangles given specific measurements."},
                        {"name": "Construct quadrilaterals", "description": "By the end of the lesson, the learner should be able to construct quadrilaterals given specific measurements."}
                    ]
                }
            ]
        },
        {
            "name": "Measurements",
            "substrands": [
                {
                    "name": "Length",
                    "slos": [
                        {"name": "Convert units of length", "description": "By the end of the lesson, the learner should be able to convert between units of length (mm, cm, m, km)."},
                        {"name": "Estimate lengths of objects", "description": "By the end of the lesson, the learner should be able to estimate lengths of objects in appropriate units."},
                        {"name": "Calculate perimeter of shapes", "description": "By the end of the lesson, the learner should be able to calculate the perimeter of different shapes."},
                        {"name": "Solve problems involving length", "description": "By the end of the lesson, the learner should be able to solve real-life problems involving length."}
                    ]
                },
                {
                    "name": "Area",
                    "slos": [
                        {"name": "Calculate area of rectangles and squares", "description": "By the end of the lesson, the learner should be able to calculate the area of rectangles and squares."},
                        {"name": "Calculate area of triangles", "description": "By the end of the lesson, the learner should be able to calculate the area of triangles."},
                        {"name": "Calculate area of parallelograms and trapeziums", "description": "By the end of the lesson, the learner should be able to calculate the area of parallelograms and trapeziums."},
                        {"name": "Calculate area of compound shapes", "description": "By the end of the lesson, the learner should be able to calculate the area of compound shapes."},
                        {"name": "Convert units of area", "description": "By the end of the lesson, the learner should be able to convert between units of area."}
                    ]
                },
                {
                    "name": "Volume and Capacity",
                    "slos": [
                        {"name": "Calculate volume of cuboids", "description": "By the end of the lesson, the learner should be able to calculate the volume of cuboids."},
                        {"name": "Calculate volume of cylinders", "description": "By the end of the lesson, the learner should be able to calculate the volume of cylinders."},
                        {"name": "Convert units of volume and capacity", "description": "By the end of the lesson, the learner should be able to convert between units of volume and capacity."},
                        {"name": "Solve problems involving volume", "description": "By the end of the lesson, the learner should be able to solve real-life problems involving volume and capacity."}
                    ]
                },
                {
                    "name": "Mass, Weight and Density",
                    "slos": [
                        {"name": "Convert units of mass", "description": "By the end of the lesson, the learner should be able to convert between units of mass (g, kg, tonnes)."},
                        {"name": "Distinguish mass from weight", "description": "By the end of the lesson, the learner should be able to distinguish between mass and weight."},
                        {"name": "Calculate density of substances", "description": "By the end of the lesson, the learner should be able to calculate the density of substances."},
                        {"name": "Solve problems involving mass and density", "description": "By the end of the lesson, the learner should be able to solve problems involving mass, weight and density."}
                    ]
                },
                {
                    "name": "Time",
                    "slos": [
                        {"name": "Convert units of time", "description": "By the end of the lesson, the learner should be able to convert between units of time."},
                        {"name": "Use 12-hour and 24-hour clock", "description": "By the end of the lesson, the learner should be able to read and convert between 12-hour and 24-hour time."},
                        {"name": "Calculate duration and time differences", "description": "By the end of the lesson, the learner should be able to calculate duration and time differences."},
                        {"name": "Solve problems involving time zones", "description": "By the end of the lesson, the learner should be able to solve problems involving different time zones."}
                    ]
                },
                {
                    "name": "Money",
                    "slos": [
                        {"name": "Perform calculations involving money", "description": "By the end of the lesson, the learner should be able to perform calculations involving money."},
                        {"name": "Calculate profit and loss", "description": "By the end of the lesson, the learner should be able to calculate profit and loss in business transactions."},
                        {"name": "Calculate simple interest", "description": "By the end of the lesson, the learner should be able to calculate simple interest on savings and loans."},
                        {"name": "Prepare simple budgets", "description": "By the end of the lesson, the learner should be able to prepare simple personal and household budgets."}
                    ]
                }
            ]
        },
        {
            "name": "Data Handling and Probability",
            "substrands": [
                {
                    "name": "Data Collection and Organization",
                    "slos": [
                        {"name": "Identify sources of data", "description": "By the end of the lesson, the learner should be able to identify primary and secondary sources of data."},
                        {"name": "Collect data using various methods", "description": "By the end of the lesson, the learner should be able to collect data using questionnaires, interviews and observations."},
                        {"name": "Organize data in tables and frequency distributions", "description": "By the end of the lesson, the learner should be able to organize data in tables and frequency distributions."},
                        {"name": "Present data using tally charts", "description": "By the end of the lesson, the learner should be able to present data using tally charts."}
                    ]
                },
                {
                    "name": "Data Representation",
                    "slos": [
                        {"name": "Draw bar graphs", "description": "By the end of the lesson, the learner should be able to draw bar graphs to represent data."},
                        {"name": "Draw pie charts", "description": "By the end of the lesson, the learner should be able to draw pie charts to represent data."},
                        {"name": "Draw line graphs", "description": "By the end of the lesson, the learner should be able to draw line graphs to represent data."},
                        {"name": "Interpret statistical graphs", "description": "By the end of the lesson, the learner should be able to interpret information from statistical graphs."}
                    ]
                },
                {
                    "name": "Measures of Central Tendency",
                    "slos": [
                        {"name": "Calculate mean of data", "description": "By the end of the lesson, the learner should be able to calculate the mean of ungrouped data."},
                        {"name": "Determine median of data", "description": "By the end of the lesson, the learner should be able to determine the median of ungrouped data."},
                        {"name": "Determine mode of data", "description": "By the end of the lesson, the learner should be able to determine the mode of ungrouped data."},
                        {"name": "Apply measures of central tendency", "description": "By the end of the lesson, the learner should be able to apply measures of central tendency in real-life situations."}
                    ]
                },
                {
                    "name": "Probability",
                    "slos": [
                        {"name": "Define probability and its terms", "description": "By the end of the lesson, the learner should be able to define probability and related terms."},
                        {"name": "Calculate probability of simple events", "description": "By the end of the lesson, the learner should be able to calculate probability of simple events."},
                        {"name": "Use probability scale", "description": "By the end of the lesson, the learner should be able to use the probability scale from 0 to 1."},
                        {"name": "Apply probability in real-life situations", "description": "By the end of the lesson, the learner should be able to apply probability in making predictions."}
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# INTEGRATED SCIENCE - GRADE 7, 8, 9 (KICD CBC Curriculum)
# ============================================================================
INTEGRATED_SCIENCE_DATA = {
    "strands": [
        {
            "name": "Living Things and Their Environment",
            "substrands": [
                {
                    "name": "Classification of Living Things",
                    "slos": [
                        {"name": "Classify living things into major groups", "description": "By the end of the lesson, the learner should be able to classify living things into major groups: plants and animals."},
                        {"name": "Identify characteristics of living things", "description": "By the end of the lesson, the learner should be able to identify characteristics of living things."},
                        {"name": "Distinguish plants from animals", "description": "By the end of the lesson, the learner should be able to distinguish plants from animals based on their characteristics."},
                        {"name": "Appreciate diversity of living things", "description": "By the end of the lesson, the learner should be able to appreciate the diversity of living things in the environment."}
                    ]
                },
                {
                    "name": "Cell Structure and Function",
                    "slos": [
                        {"name": "Identify parts of a cell", "description": "By the end of the lesson, the learner should be able to identify parts of plant and animal cells."},
                        {"name": "Describe functions of cell parts", "description": "By the end of the lesson, the learner should be able to describe the functions of cell parts."},
                        {"name": "Distinguish plant cells from animal cells", "description": "By the end of the lesson, the learner should be able to distinguish plant cells from animal cells."},
                        {"name": "Observe cells under a microscope", "description": "By the end of the lesson, the learner should be able to observe cells under a microscope."}
                    ]
                },
                {
                    "name": "Ecosystems",
                    "slos": [
                        {"name": "Define ecosystem and its components", "description": "By the end of the lesson, the learner should be able to define ecosystem and identify its components."},
                        {"name": "Describe food chains and food webs", "description": "By the end of the lesson, the learner should be able to describe food chains and food webs in an ecosystem."},
                        {"name": "Explain energy flow in ecosystems", "description": "By the end of the lesson, the learner should be able to explain energy flow in ecosystems."},
                        {"name": "Identify factors affecting ecosystems", "description": "By the end of the lesson, the learner should be able to identify factors affecting ecosystems."},
                        {"name": "Appreciate importance of conserving ecosystems", "description": "By the end of the lesson, the learner should be able to appreciate the importance of conserving ecosystems."}
                    ]
                },
                {
                    "name": "Human Body Systems",
                    "slos": [
                        {"name": "Describe the digestive system", "description": "By the end of the lesson, the learner should be able to describe the structure and function of the digestive system."},
                        {"name": "Describe the respiratory system", "description": "By the end of the lesson, the learner should be able to describe the structure and function of the respiratory system."},
                        {"name": "Describe the circulatory system", "description": "By the end of the lesson, the learner should be able to describe the structure and function of the circulatory system."},
                        {"name": "Explain the importance of body systems", "description": "By the end of the lesson, the learner should be able to explain the importance of maintaining healthy body systems."}
                    ]
                },
                {
                    "name": "Reproduction in Living Things",
                    "slos": [
                        {"name": "Describe reproduction in plants", "description": "By the end of the lesson, the learner should be able to describe sexual and asexual reproduction in plants."},
                        {"name": "Describe reproduction in animals", "description": "By the end of the lesson, the learner should be able to describe reproduction in animals."},
                        {"name": "Explain human reproductive system", "description": "By the end of the lesson, the learner should be able to explain the human reproductive system."},
                        {"name": "Discuss adolescent changes", "description": "By the end of the lesson, the learner should be able to discuss physical and emotional changes during adolescence."}
                    ]
                }
            ]
        },
        {
            "name": "Matter and Materials",
            "substrands": [
                {
                    "name": "States of Matter",
                    "slos": [
                        {"name": "Identify states of matter", "description": "By the end of the lesson, the learner should be able to identify the three states of matter: solid, liquid and gas."},
                        {"name": "Describe properties of each state", "description": "By the end of the lesson, the learner should be able to describe properties of solids, liquids and gases."},
                        {"name": "Explain changes of state", "description": "By the end of the lesson, the learner should be able to explain changes of state (melting, freezing, evaporation, condensation)."},
                        {"name": "Investigate factors affecting changes of state", "description": "By the end of the lesson, the learner should be able to investigate factors affecting changes of state."}
                    ]
                },
                {
                    "name": "Mixtures and Compounds",
                    "slos": [
                        {"name": "Distinguish mixtures from compounds", "description": "By the end of the lesson, the learner should be able to distinguish between mixtures and compounds."},
                        {"name": "Identify types of mixtures", "description": "By the end of the lesson, the learner should be able to identify homogeneous and heterogeneous mixtures."},
                        {"name": "Separate components of mixtures", "description": "By the end of the lesson, the learner should be able to separate components of mixtures using various methods."},
                        {"name": "Apply separation techniques", "description": "By the end of the lesson, the learner should be able to apply separation techniques in real-life situations."}
                    ]
                },
                {
                    "name": "Elements and Atoms",
                    "slos": [
                        {"name": "Define elements and atoms", "description": "By the end of the lesson, the learner should be able to define elements and atoms."},
                        {"name": "Identify common elements", "description": "By the end of the lesson, the learner should be able to identify common elements and their symbols."},
                        {"name": "Describe atomic structure", "description": "By the end of the lesson, the learner should be able to describe the basic structure of an atom."},
                        {"name": "Use the periodic table", "description": "By the end of the lesson, the learner should be able to use the periodic table to identify elements."}
                    ]
                },
                {
                    "name": "Chemical Reactions",
                    "slos": [
                        {"name": "Identify signs of chemical reactions", "description": "By the end of the lesson, the learner should be able to identify signs of chemical reactions."},
                        {"name": "Distinguish physical from chemical changes", "description": "By the end of the lesson, the learner should be able to distinguish physical changes from chemical changes."},
                        {"name": "Describe types of chemical reactions", "description": "By the end of the lesson, the learner should be able to describe types of chemical reactions."},
                        {"name": "Write simple chemical equations", "description": "By the end of the lesson, the learner should be able to write simple word equations for chemical reactions."}
                    ]
                },
                {
                    "name": "Acids and Bases",
                    "slos": [
                        {"name": "Identify acids and bases", "description": "By the end of the lesson, the learner should be able to identify acids and bases using indicators."},
                        {"name": "Describe properties of acids and bases", "description": "By the end of the lesson, the learner should be able to describe properties of acids and bases."},
                        {"name": "Measure pH of substances", "description": "By the end of the lesson, the learner should be able to measure pH of substances using pH scale."},
                        {"name": "Apply knowledge of acids and bases", "description": "By the end of the lesson, the learner should be able to apply knowledge of acids and bases in daily life."}
                    ]
                }
            ]
        },
        {
            "name": "Energy and Forces",
            "substrands": [
                {
                    "name": "Forms of Energy",
                    "slos": [
                        {"name": "Identify forms of energy", "description": "By the end of the lesson, the learner should be able to identify different forms of energy."},
                        {"name": "Describe energy transformations", "description": "By the end of the lesson, the learner should be able to describe energy transformations in daily life."},
                        {"name": "Explain law of conservation of energy", "description": "By the end of the lesson, the learner should be able to explain the law of conservation of energy."},
                        {"name": "Discuss renewable and non-renewable energy", "description": "By the end of the lesson, the learner should be able to discuss renewable and non-renewable energy sources."}
                    ]
                },
                {
                    "name": "Heat Energy",
                    "slos": [
                        {"name": "Define heat and temperature", "description": "By the end of the lesson, the learner should be able to define heat and temperature."},
                        {"name": "Describe modes of heat transfer", "description": "By the end of the lesson, the learner should be able to describe conduction, convection and radiation."},
                        {"name": "Investigate factors affecting heat transfer", "description": "By the end of the lesson, the learner should be able to investigate factors affecting heat transfer."},
                        {"name": "Apply knowledge of heat transfer", "description": "By the end of the lesson, the learner should be able to apply knowledge of heat transfer in daily life."}
                    ]
                },
                {
                    "name": "Light Energy",
                    "slos": [
                        {"name": "Describe properties of light", "description": "By the end of the lesson, the learner should be able to describe properties of light."},
                        {"name": "Explain reflection and refraction", "description": "By the end of the lesson, the learner should be able to explain reflection and refraction of light."},
                        {"name": "Describe formation of shadows", "description": "By the end of the lesson, the learner should be able to describe the formation of shadows."},
                        {"name": "Explain the working of optical instruments", "description": "By the end of the lesson, the learner should be able to explain the working of simple optical instruments."}
                    ]
                },
                {
                    "name": "Sound Energy",
                    "slos": [
                        {"name": "Describe how sound is produced", "description": "By the end of the lesson, the learner should be able to describe how sound is produced."},
                        {"name": "Explain propagation of sound", "description": "By the end of the lesson, the learner should be able to explain how sound travels through different media."},
                        {"name": "Identify characteristics of sound", "description": "By the end of the lesson, the learner should be able to identify pitch, loudness and quality of sound."},
                        {"name": "Discuss effects of noise pollution", "description": "By the end of the lesson, the learner should be able to discuss effects and control of noise pollution."}
                    ]
                },
                {
                    "name": "Electrical Energy",
                    "slos": [
                        {"name": "Describe sources of electricity", "description": "By the end of the lesson, the learner should be able to describe sources of electricity."},
                        {"name": "Explain electric circuits", "description": "By the end of the lesson, the learner should be able to explain simple electric circuits."},
                        {"name": "Describe conductors and insulators", "description": "By the end of the lesson, the learner should be able to describe electrical conductors and insulators."},
                        {"name": "Practice electrical safety", "description": "By the end of the lesson, the learner should be able to practice electrical safety measures."}
                    ]
                },
                {
                    "name": "Forces and Motion",
                    "slos": [
                        {"name": "Define force and its effects", "description": "By the end of the lesson, the learner should be able to define force and describe its effects on objects."},
                        {"name": "Identify types of forces", "description": "By the end of the lesson, the learner should be able to identify different types of forces."},
                        {"name": "Describe motion and its types", "description": "By the end of the lesson, the learner should be able to describe motion and its types."},
                        {"name": "Calculate speed and velocity", "description": "By the end of the lesson, the learner should be able to calculate speed and velocity of moving objects."},
                        {"name": "Apply Newton's laws of motion", "description": "By the end of the lesson, the learner should be able to apply Newton's laws of motion to everyday situations."}
                    ]
                }
            ]
        },
        {
            "name": "Earth and Space",
            "substrands": [
                {
                    "name": "The Solar System",
                    "slos": [
                        {"name": "Describe components of the solar system", "description": "By the end of the lesson, the learner should be able to describe the sun, planets and other components of the solar system."},
                        {"name": "Explain movements of the Earth", "description": "By the end of the lesson, the learner should be able to explain rotation and revolution of the Earth."},
                        {"name": "Describe phases of the moon", "description": "By the end of the lesson, the learner should be able to describe the phases of the moon."},
                        {"name": "Explain eclipses", "description": "By the end of the lesson, the learner should be able to explain solar and lunar eclipses."}
                    ]
                },
                {
                    "name": "Weather and Climate",
                    "slos": [
                        {"name": "Distinguish weather from climate", "description": "By the end of the lesson, the learner should be able to distinguish between weather and climate."},
                        {"name": "Identify elements of weather", "description": "By the end of the lesson, the learner should be able to identify and measure elements of weather."},
                        {"name": "Describe factors affecting climate", "description": "By the end of the lesson, the learner should be able to describe factors affecting climate."},
                        {"name": "Discuss effects of climate change", "description": "By the end of the lesson, the learner should be able to discuss causes and effects of climate change."}
                    ]
                },
                {
                    "name": "Rocks and Minerals",
                    "slos": [
                        {"name": "Classify rocks into types", "description": "By the end of the lesson, the learner should be able to classify rocks into igneous, sedimentary and metamorphic."},
                        {"name": "Describe the rock cycle", "description": "By the end of the lesson, the learner should be able to describe the rock cycle."},
                        {"name": "Identify common minerals", "description": "By the end of the lesson, the learner should be able to identify common minerals and their uses."},
                        {"name": "Discuss importance of rocks and minerals", "description": "By the end of the lesson, the learner should be able to discuss importance of rocks and minerals in Kenya."}
                    ]
                },
                {
                    "name": "Water Resources",
                    "slos": [
                        {"name": "Describe the water cycle", "description": "By the end of the lesson, the learner should be able to describe the water cycle."},
                        {"name": "Identify sources of water", "description": "By the end of the lesson, the learner should be able to identify sources of water."},
                        {"name": "Discuss water conservation", "description": "By the end of the lesson, the learner should be able to discuss methods of water conservation."},
                        {"name": "Explain water treatment", "description": "By the end of the lesson, the learner should be able to explain water treatment and purification methods."}
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# SOCIAL STUDIES - GRADE 7, 8, 9 (KICD CBC Curriculum)
# ============================================================================
SOCIAL_STUDIES_DATA = {
    "strands": [
        {
            "name": "Environment and Resources",
            "substrands": [
                {
                    "name": "Physical Features of Kenya",
                    "slos": [
                        {"name": "Identify physical features of Kenya", "description": "By the end of the lesson, the learner should be able to identify major physical features of Kenya."},
                        {"name": "Describe formation of physical features", "description": "By the end of the lesson, the learner should be able to describe how physical features were formed."},
                        {"name": "Explain significance of physical features", "description": "By the end of the lesson, the learner should be able to explain the significance of physical features to human activities."},
                        {"name": "Locate physical features on a map", "description": "By the end of the lesson, the learner should be able to locate major physical features on a map of Kenya."}
                    ]
                },
                {
                    "name": "Climate of Kenya",
                    "slos": [
                        {"name": "Describe climate regions of Kenya", "description": "By the end of the lesson, the learner should be able to describe the different climate regions of Kenya."},
                        {"name": "Explain factors influencing climate", "description": "By the end of the lesson, the learner should be able to explain factors that influence climate in Kenya."},
                        {"name": "Discuss effects of climate on human activities", "description": "By the end of the lesson, the learner should be able to discuss effects of climate on human activities."},
                        {"name": "Analyze climate change impacts", "description": "By the end of the lesson, the learner should be able to analyze impacts of climate change in Kenya."}
                    ]
                },
                {
                    "name": "Natural Resources",
                    "slos": [
                        {"name": "Identify natural resources in Kenya", "description": "By the end of the lesson, the learner should be able to identify natural resources found in Kenya."},
                        {"name": "Classify natural resources", "description": "By the end of the lesson, the learner should be able to classify natural resources as renewable and non-renewable."},
                        {"name": "Explain importance of natural resources", "description": "By the end of the lesson, the learner should be able to explain the importance of natural resources to Kenya's economy."},
                        {"name": "Discuss conservation of resources", "description": "By the end of the lesson, the learner should be able to discuss ways of conserving natural resources."}
                    ]
                },
                {
                    "name": "Environmental Conservation",
                    "slos": [
                        {"name": "Identify environmental problems", "description": "By the end of the lesson, the learner should be able to identify environmental problems in Kenya."},
                        {"name": "Explain causes of environmental degradation", "description": "By the end of the lesson, the learner should be able to explain causes of environmental degradation."},
                        {"name": "Discuss conservation measures", "description": "By the end of the lesson, the learner should be able to discuss environmental conservation measures."},
                        {"name": "Participate in environmental activities", "description": "By the end of the lesson, the learner should be able to participate in environmental conservation activities."}
                    ]
                }
            ]
        },
        {
            "name": "Population and Settlement",
            "substrands": [
                {
                    "name": "Population of Kenya",
                    "slos": [
                        {"name": "Describe population distribution in Kenya", "description": "By the end of the lesson, the learner should be able to describe population distribution in Kenya."},
                        {"name": "Explain factors influencing population distribution", "description": "By the end of the lesson, the learner should be able to explain factors influencing population distribution."},
                        {"name": "Analyze population growth trends", "description": "By the end of the lesson, the learner should be able to analyze population growth trends in Kenya."},
                        {"name": "Discuss effects of population growth", "description": "By the end of the lesson, the learner should be able to discuss effects of population growth on resources."}
                    ]
                },
                {
                    "name": "Migration",
                    "slos": [
                        {"name": "Define migration and its types", "description": "By the end of the lesson, the learner should be able to define migration and identify its types."},
                        {"name": "Explain causes of migration", "description": "By the end of the lesson, the learner should be able to explain causes of rural-urban migration."},
                        {"name": "Discuss effects of migration", "description": "By the end of the lesson, the learner should be able to discuss effects of migration on source and destination areas."},
                        {"name": "Propose solutions to migration problems", "description": "By the end of the lesson, the learner should be able to propose solutions to problems caused by migration."}
                    ]
                },
                {
                    "name": "Settlement Patterns",
                    "slos": [
                        {"name": "Identify settlement patterns in Kenya", "description": "By the end of the lesson, the learner should be able to identify different settlement patterns in Kenya."},
                        {"name": "Explain factors influencing settlement", "description": "By the end of the lesson, the learner should be able to explain factors influencing settlement patterns."},
                        {"name": "Compare rural and urban settlements", "description": "By the end of the lesson, the learner should be able to compare characteristics of rural and urban settlements."},
                        {"name": "Discuss urbanization challenges", "description": "By the end of the lesson, the learner should be able to discuss challenges of urbanization in Kenya."}
                    ]
                }
            ]
        },
        {
            "name": "History and Government",
            "substrands": [
                {
                    "name": "Pre-Colonial Kenya",
                    "slos": [
                        {"name": "Describe early communities in Kenya", "description": "By the end of the lesson, the learner should be able to describe early communities in Kenya."},
                        {"name": "Explain migration and settlement of communities", "description": "By the end of the lesson, the learner should be able to explain migration and settlement of various communities."},
                        {"name": "Describe social organization of communities", "description": "By the end of the lesson, the learner should be able to describe social organization of Kenyan communities."},
                        {"name": "Discuss economic activities of early communities", "description": "By the end of the lesson, the learner should be able to discuss economic activities of early Kenyan communities."}
                    ]
                },
                {
                    "name": "Colonial Period in Kenya",
                    "slos": [
                        {"name": "Explain establishment of colonial rule", "description": "By the end of the lesson, the learner should be able to explain how colonial rule was established in Kenya."},
                        {"name": "Describe effects of colonialism", "description": "By the end of the lesson, the learner should be able to describe social, economic and political effects of colonialism."},
                        {"name": "Discuss African resistance to colonialism", "description": "By the end of the lesson, the learner should be able to discuss African resistance to colonial rule."},
                        {"name": "Explain struggle for independence", "description": "By the end of the lesson, the learner should be able to explain the struggle for independence in Kenya."}
                    ]
                },
                {
                    "name": "Independent Kenya",
                    "slos": [
                        {"name": "Describe attainment of independence", "description": "By the end of the lesson, the learner should be able to describe the attainment of independence in Kenya."},
                        {"name": "Explain political developments since independence", "description": "By the end of the lesson, the learner should be able to explain major political developments since independence."},
                        {"name": "Discuss challenges facing independent Kenya", "description": "By the end of the lesson, the learner should be able to discuss challenges facing independent Kenya."},
                        {"name": "Identify national heroes and heroines", "description": "By the end of the lesson, the learner should be able to identify and appreciate national heroes and heroines."}
                    ]
                },
                {
                    "name": "Government of Kenya",
                    "slos": [
                        {"name": "Describe the structure of government", "description": "By the end of the lesson, the learner should be able to describe the structure of the Kenya government."},
                        {"name": "Explain functions of government organs", "description": "By the end of the lesson, the learner should be able to explain functions of the executive, legislature and judiciary."},
                        {"name": "Discuss devolution in Kenya", "description": "By the end of the lesson, the learner should be able to discuss devolution and county governments."},
                        {"name": "Explain citizen participation in governance", "description": "By the end of the lesson, the learner should be able to explain ways of citizen participation in governance."}
                    ]
                }
            ]
        },
        {
            "name": "Economic Activities",
            "substrands": [
                {
                    "name": "Agriculture",
                    "slos": [
                        {"name": "Describe types of farming in Kenya", "description": "By the end of the lesson, the learner should be able to describe types of farming practiced in Kenya."},
                        {"name": "Explain factors influencing agriculture", "description": "By the end of the lesson, the learner should be able to explain factors influencing agriculture in Kenya."},
                        {"name": "Discuss contribution of agriculture to economy", "description": "By the end of the lesson, the learner should be able to discuss contribution of agriculture to Kenya's economy."},
                        {"name": "Identify challenges in agriculture", "description": "By the end of the lesson, the learner should be able to identify challenges facing agriculture in Kenya."}
                    ]
                },
                {
                    "name": "Trade and Industry",
                    "slos": [
                        {"name": "Define trade and its types", "description": "By the end of the lesson, the learner should be able to define trade and identify its types."},
                        {"name": "Describe Kenya's trade relations", "description": "By the end of the lesson, the learner should be able to describe Kenya's trade relations with other countries."},
                        {"name": "Explain industrialization in Kenya", "description": "By the end of the lesson, the learner should be able to explain industrialization in Kenya."},
                        {"name": "Discuss role of trade and industry in economy", "description": "By the end of the lesson, the learner should be able to discuss role of trade and industry in Kenya's economy."}
                    ]
                },
                {
                    "name": "Transport and Communication",
                    "slos": [
                        {"name": "Identify modes of transport in Kenya", "description": "By the end of the lesson, the learner should be able to identify different modes of transport in Kenya."},
                        {"name": "Explain importance of transport", "description": "By the end of the lesson, the learner should be able to explain importance of transport in economic development."},
                        {"name": "Describe communication systems in Kenya", "description": "By the end of the lesson, the learner should be able to describe communication systems in Kenya."},
                        {"name": "Discuss challenges in transport sector", "description": "By the end of the lesson, the learner should be able to discuss challenges facing the transport sector."}
                    ]
                },
                {
                    "name": "Tourism",
                    "slos": [
                        {"name": "Identify tourist attractions in Kenya", "description": "By the end of the lesson, the learner should be able to identify major tourist attractions in Kenya."},
                        {"name": "Explain factors promoting tourism", "description": "By the end of the lesson, the learner should be able to explain factors that promote tourism in Kenya."},
                        {"name": "Discuss contribution of tourism to economy", "description": "By the end of the lesson, the learner should be able to discuss contribution of tourism to Kenya's economy."},
                        {"name": "Analyze challenges facing tourism", "description": "By the end of the lesson, the learner should be able to analyze challenges facing the tourism industry."}
                    ]
                }
            ]
        },
        {
            "name": "Citizenship and Values",
            "substrands": [
                {
                    "name": "Rights and Responsibilities",
                    "slos": [
                        {"name": "Identify rights of citizens", "description": "By the end of the lesson, the learner should be able to identify rights of citizens as outlined in the constitution."},
                        {"name": "Explain responsibilities of citizens", "description": "By the end of the lesson, the learner should be able to explain responsibilities of citizens."},
                        {"name": "Discuss importance of respecting rights", "description": "By the end of the lesson, the learner should be able to discuss importance of respecting the rights of others."},
                        {"name": "Demonstrate responsible citizenship", "description": "By the end of the lesson, the learner should be able to demonstrate responsible citizenship in daily life."}
                    ]
                },
                {
                    "name": "National Unity",
                    "slos": [
                        {"name": "Identify national symbols", "description": "By the end of the lesson, the learner should be able to identify national symbols and their significance."},
                        {"name": "Explain importance of national unity", "description": "By the end of the lesson, the learner should be able to explain importance of national unity."},
                        {"name": "Discuss factors promoting national unity", "description": "By the end of the lesson, the learner should be able to discuss factors that promote national unity."},
                        {"name": "Participate in activities promoting unity", "description": "By the end of the lesson, the learner should be able to participate in activities that promote national unity."}
                    ]
                },
                {
                    "name": "Peace and Security",
                    "slos": [
                        {"name": "Define peace and security", "description": "By the end of the lesson, the learner should be able to define peace and security."},
                        {"name": "Identify threats to peace", "description": "By the end of the lesson, the learner should be able to identify threats to peace and security."},
                        {"name": "Discuss conflict resolution methods", "description": "By the end of the lesson, the learner should be able to discuss methods of conflict resolution."},
                        {"name": "Promote peace in the community", "description": "By the end of the lesson, the learner should be able to promote peace in the school and community."}
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# PRE-TECHNICAL STUDIES - GRADE 7, 8, 9 (KICD CBC Curriculum)
# ============================================================================
PRE_TECHNICAL_STUDIES_DATA = {
    "strands": [
        {
            "name": "Drawing and Design",
            "substrands": [
                {
                    "name": "Technical Drawing Basics",
                    "slos": [
                        {"name": "Identify drawing instruments", "description": "By the end of the lesson, the learner should be able to identify and use drawing instruments correctly."},
                        {"name": "Draw different types of lines", "description": "By the end of the lesson, the learner should be able to draw different types of lines used in technical drawing."},
                        {"name": "Construct geometric shapes", "description": "By the end of the lesson, the learner should be able to construct basic geometric shapes."},
                        {"name": "Apply lettering techniques", "description": "By the end of the lesson, the learner should be able to apply lettering techniques in technical drawing."}
                    ]
                },
                {
                    "name": "Pictorial Drawing",
                    "slos": [
                        {"name": "Draw objects in isometric projection", "description": "By the end of the lesson, the learner should be able to draw objects in isometric projection."},
                        {"name": "Draw objects in oblique projection", "description": "By the end of the lesson, the learner should be able to draw objects in oblique projection."},
                        {"name": "Convert views to pictorial drawings", "description": "By the end of the lesson, the learner should be able to convert orthographic views to pictorial drawings."},
                        {"name": "Apply shading techniques", "description": "By the end of the lesson, the learner should be able to apply shading techniques to pictorial drawings."}
                    ]
                },
                {
                    "name": "Orthographic Projection",
                    "slos": [
                        {"name": "Explain orthographic projection", "description": "By the end of the lesson, the learner should be able to explain orthographic projection."},
                        {"name": "Draw first angle projection", "description": "By the end of the lesson, the learner should be able to draw objects in first angle projection."},
                        {"name": "Draw third angle projection", "description": "By the end of the lesson, the learner should be able to draw objects in third angle projection."},
                        {"name": "Interpret orthographic drawings", "description": "By the end of the lesson, the learner should be able to interpret orthographic drawings."}
                    ]
                }
            ]
        },
        {
            "name": "Woodwork Technology",
            "substrands": [
                {
                    "name": "Wood and Wood Products",
                    "slos": [
                        {"name": "Identify types of wood", "description": "By the end of the lesson, the learner should be able to identify softwood and hardwood types."},
                        {"name": "Describe properties of wood", "description": "By the end of the lesson, the learner should be able to describe properties of different types of wood."},
                        {"name": "Explain wood conversion and seasoning", "description": "By the end of the lesson, the learner should be able to explain wood conversion and seasoning methods."},
                        {"name": "Identify wood defects", "description": "By the end of the lesson, the learner should be able to identify common wood defects and their causes."}
                    ]
                },
                {
                    "name": "Woodwork Tools",
                    "slos": [
                        {"name": "Identify woodwork hand tools", "description": "By the end of the lesson, the learner should be able to identify and use woodwork hand tools."},
                        {"name": "Use measuring and marking tools", "description": "By the end of the lesson, the learner should be able to use measuring and marking tools correctly."},
                        {"name": "Maintain woodwork tools", "description": "By the end of the lesson, the learner should be able to maintain woodwork tools properly."},
                        {"name": "Observe safety in using tools", "description": "By the end of the lesson, the learner should be able to observe safety precautions when using woodwork tools."}
                    ]
                },
                {
                    "name": "Wood Joints",
                    "slos": [
                        {"name": "Identify types of wood joints", "description": "By the end of the lesson, the learner should be able to identify different types of wood joints."},
                        {"name": "Construct simple wood joints", "description": "By the end of the lesson, the learner should be able to construct simple wood joints."},
                        {"name": "Select appropriate joints for projects", "description": "By the end of the lesson, the learner should be able to select appropriate joints for different projects."},
                        {"name": "Apply joints in making articles", "description": "By the end of the lesson, the learner should be able to apply wood joints in making simple articles."}
                    ]
                }
            ]
        },
        {
            "name": "Metalwork Technology",
            "substrands": [
                {
                    "name": "Metals and Alloys",
                    "slos": [
                        {"name": "Classify metals", "description": "By the end of the lesson, the learner should be able to classify metals into ferrous and non-ferrous."},
                        {"name": "Describe properties of metals", "description": "By the end of the lesson, the learner should be able to describe properties of common metals."},
                        {"name": "Identify common alloys", "description": "By the end of the lesson, the learner should be able to identify common alloys and their uses."},
                        {"name": "Explain metal extraction processes", "description": "By the end of the lesson, the learner should be able to explain basic metal extraction processes."}
                    ]
                },
                {
                    "name": "Metalwork Tools",
                    "slos": [
                        {"name": "Identify metalwork hand tools", "description": "By the end of the lesson, the learner should be able to identify metalwork hand tools and their uses."},
                        {"name": "Use measuring tools in metalwork", "description": "By the end of the lesson, the learner should be able to use measuring tools in metalwork."},
                        {"name": "Perform basic metalwork operations", "description": "By the end of the lesson, the learner should be able to perform basic metalwork operations."},
                        {"name": "Observe safety in metalwork", "description": "By the end of the lesson, the learner should be able to observe safety precautions in metalwork."}
                    ]
                },
                {
                    "name": "Metal Joining",
                    "slos": [
                        {"name": "Identify metal joining methods", "description": "By the end of the lesson, the learner should be able to identify different metal joining methods."},
                        {"name": "Perform soldering operations", "description": "By the end of the lesson, the learner should be able to perform simple soldering operations."},
                        {"name": "Describe welding processes", "description": "By the end of the lesson, the learner should be able to describe basic welding processes."},
                        {"name": "Join metals using appropriate methods", "description": "By the end of the lesson, the learner should be able to join metals using appropriate methods."}
                    ]
                }
            ]
        },
        {
            "name": "Power and Energy",
            "substrands": [
                {
                    "name": "Sources of Energy",
                    "slos": [
                        {"name": "Identify sources of energy", "description": "By the end of the lesson, the learner should be able to identify conventional and alternative sources of energy."},
                        {"name": "Explain renewable energy sources", "description": "By the end of the lesson, the learner should be able to explain renewable energy sources and their uses."},
                        {"name": "Discuss energy conservation", "description": "By the end of the lesson, the learner should be able to discuss methods of energy conservation."},
                        {"name": "Apply energy in simple projects", "description": "By the end of the lesson, the learner should be able to apply different energy sources in simple projects."}
                    ]
                },
                {
                    "name": "Electrical Systems",
                    "slos": [
                        {"name": "Describe basic electrical concepts", "description": "By the end of the lesson, the learner should be able to describe basic electrical concepts."},
                        {"name": "Identify electrical components", "description": "By the end of the lesson, the learner should be able to identify common electrical components."},
                        {"name": "Construct simple electrical circuits", "description": "By the end of the lesson, the learner should be able to construct simple electrical circuits."},
                        {"name": "Practice electrical safety", "description": "By the end of the lesson, the learner should be able to practice electrical safety measures."}
                    ]
                },
                {
                    "name": "Simple Machines",
                    "slos": [
                        {"name": "Identify types of simple machines", "description": "By the end of the lesson, the learner should be able to identify types of simple machines."},
                        {"name": "Explain mechanical advantage", "description": "By the end of the lesson, the learner should be able to explain mechanical advantage of simple machines."},
                        {"name": "Calculate efficiency of machines", "description": "By the end of the lesson, the learner should be able to calculate efficiency of simple machines."},
                        {"name": "Apply simple machines in daily life", "description": "By the end of the lesson, the learner should be able to apply knowledge of simple machines in daily life."}
                    ]
                }
            ]
        },
        {
            "name": "Building Technology",
            "substrands": [
                {
                    "name": "Building Materials",
                    "slos": [
                        {"name": "Identify building materials", "description": "By the end of the lesson, the learner should be able to identify common building materials."},
                        {"name": "Describe properties of building materials", "description": "By the end of the lesson, the learner should be able to describe properties of building materials."},
                        {"name": "Select appropriate materials for construction", "description": "By the end of the lesson, the learner should be able to select appropriate materials for construction."},
                        {"name": "Discuss sustainable building materials", "description": "By the end of the lesson, the learner should be able to discuss sustainable building materials."}
                    ]
                },
                {
                    "name": "Building Processes",
                    "slos": [
                        {"name": "Explain foundation construction", "description": "By the end of the lesson, the learner should be able to explain foundation construction processes."},
                        {"name": "Describe walling methods", "description": "By the end of the lesson, the learner should be able to describe different walling methods."},
                        {"name": "Explain roofing techniques", "description": "By the end of the lesson, the learner should be able to explain basic roofing techniques."},
                        {"name": "Discuss finishing processes", "description": "By the end of the lesson, the learner should be able to discuss finishing processes in construction."}
                    ]
                }
            ]
        }
    ]
}


async def get_or_create_grade(name, order):
    """Get or create a grade and return its ID"""
    grade = await db.grades.find_one({"name": name})
    if grade:
        return grade.get('id', str(grade['_id']))
    
    grade_id = str(ObjectId())
    await db.grades.insert_one({
        "id": grade_id,
        "name": name,
        "order": order
    })
    print(f"  Created grade: {name}")
    return grade_id


async def seed_subject(subject_name, subject_data, grade_ids):
    """Seed a subject with strands, substrands, and SLOs"""
    print(f"\n--- Seeding {subject_name} for Grades {len(grade_ids)} ---")
    
    # Check if subject already has content
    existing_subject = await db.subjects.find_one({"name": subject_name})
    if existing_subject:
        subject_id = existing_subject.get('id', str(existing_subject['_id']))
        existing_strands = await db.strands.count_documents({"subjectId": subject_id})
        if existing_strands > 0:
            print(f"  Subject already has {existing_strands} strands. Skipping...")
            return 0, 0, 0
        
        # Update grade IDs if needed
        current_grades = set(existing_subject.get('gradeIds', []))
        new_grades = set(grade_ids)
        if new_grades - current_grades:
            await db.subjects.update_one(
                {"name": subject_name},
                {"$addToSet": {"gradeIds": {"$each": list(new_grades)}}}
            )
            print(f"  Updated grades for existing subject")
    else:
        # Create new subject
        subject_id = str(ObjectId())
        await db.subjects.insert_one({
            "id": subject_id,
            "name": subject_name,
            "gradeIds": grade_ids
        })
        print(f"  Created new subject: {subject_name}")
    
    strands_count = 0
    substrands_count = 0
    slos_count = 0
    
    for strand_data in subject_data["strands"]:
        strand_id = str(ObjectId())
        await db.strands.insert_one({
            "id": strand_id,
            "name": strand_data["name"],
            "subjectId": subject_id
        })
        strands_count += 1
        
        for substrand_data in strand_data["substrands"]:
            substrand_id = str(ObjectId())
            await db.substrands.insert_one({
                "id": substrand_id,
                "name": substrand_data["name"],
                "strandId": strand_id
            })
            substrands_count += 1
            
            for slo_data in substrand_data["slos"]:
                await db.slos.insert_one({
                    "id": str(ObjectId()),
                    "name": slo_data["name"],
                    "description": slo_data["description"],
                    "substrandId": substrand_id
                })
                slos_count += 1
    
    print(f"  Added: {strands_count} strands, {substrands_count} substrands, {slos_count} SLOs")
    return strands_count, substrands_count, slos_count


async def main():
    """Main function to seed Junior Secondary curriculum data"""
    print("=" * 70)
    print("SEEDING JUNIOR SECONDARY CURRICULUM (Grades 7, 8, 9)")
    print("Subjects: Mathematics, Integrated Science, Social Studies, Pre-Technical Studies")
    print("=" * 70)
    
    # Get or create grades 7, 8, 9
    grade_7_id = await get_or_create_grade("Grade 7", 7)
    grade_8_id = await get_or_create_grade("Grade 8", 8)
    grade_9_id = await get_or_create_grade("Grade 9", 9)
    
    junior_secondary_grades = [grade_7_id, grade_8_id, grade_9_id]
    
    print(f"\nGrade IDs: 7={grade_7_id[:8]}..., 8={grade_8_id[:8]}..., 9={grade_9_id[:8]}...")
    
    total_strands = 0
    total_substrands = 0
    total_slos = 0
    
    # Seed each subject
    subjects_to_seed = [
        ("Mathematics", MATHEMATICS_DATA),
        ("Integrated Science", INTEGRATED_SCIENCE_DATA),
        ("Social Studies", SOCIAL_STUDIES_DATA),
        ("Pre-Technical Studies", PRE_TECHNICAL_STUDIES_DATA)
    ]
    
    for subject_name, subject_data in subjects_to_seed:
        s, ss, slo = await seed_subject(subject_name, subject_data, junior_secondary_grades)
        total_strands += s
        total_substrands += ss
        total_slos += slo
    
    print("\n" + "=" * 70)
    print("SEEDING COMPLETE")
    print("=" * 70)
    print(f"Total Strands Added: {total_strands}")
    print(f"Total Substrands Added: {total_substrands}")
    print(f"Total SLOs Added: {total_slos}")
    
    # Verify totals
    print("\n=== Database Totals ===")
    subjects_count = await db.subjects.count_documents({})
    strands_count = await db.strands.count_documents({})
    substrands_count = await db.substrands.count_documents({})
    slos_count = await db.slos.count_documents({})
    
    print(f"  Subjects: {subjects_count}")
    print(f"  Strands: {strands_count}")
    print(f"  Substrands: {substrands_count}")
    print(f"  SLOs: {slos_count}")


if __name__ == "__main__":
    asyncio.run(main())
