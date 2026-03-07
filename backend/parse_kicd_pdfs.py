#!/usr/bin/env python3
"""
Parse KICD Junior Secondary Curriculum Design PDFs and extract:
- Strands
- Sub-strands  
- Specific Learning Outcomes (SLOs)

Then seed into MongoDB database.
"""

import fitz  # PyMuPDF
import re
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


def extract_text_from_pdf(pdf_path):
    """Extract all text from PDF"""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    return full_text


def parse_mathematics_curriculum(text):
    """Parse Mathematics curriculum from extracted text"""
    strands = []
    
    # Define the strands based on KICD Mathematics curriculum
    strand_definitions = [
        {
            "name": "Numbers",
            "substrands": [
                {"name": "Whole Numbers", "slos": [
                    {"name": "Use place value and total value of digits", "description": "By the end of the sub strand, the learner should be able to use place value and total value of digits up to hundreds of millions."},
                    {"name": "Read and write numbers in symbols and words", "description": "By the end of the sub strand, the learner should be able to read and write numbers in symbols up to hundreds of millions and words up to millions."},
                    {"name": "Classify natural numbers", "description": "By the end of the sub strand, the learner should be able to classify natural numbers as even, odd and prime."},
                    {"name": "Apply operations of whole numbers", "description": "By the end of the sub strand, the learner should be able to apply operations of whole numbers in real life situations."},
                    {"name": "Identify and create number sequences", "description": "By the end of the sub strand, the learner should be able to identify and create number sequences in different situations."},
                ]},
                {"name": "Factors and Multiples", "slos": [
                    {"name": "Test divisibility of numbers", "description": "By the end of the sub strand, the learner should be able to test divisibility of numbers by 2, 3, 4, 5, 6, 8, 9, 10 and 11."},
                    {"name": "Express composite numbers as product of prime factors", "description": "By the end of the sub strand, the learner should be able to express composite numbers as a product of prime factors."},
                    {"name": "Work out GCD and LCM", "description": "By the end of the sub strand, the learner should be able to work out and apply the Greatest Common Divisor (GCD) and Least Common Multiple (LCM) of numbers."},
                ]},
                {"name": "Fractions", "slos": [
                    {"name": "Add, subtract and multiply fractions", "description": "By the end of the sub strand, the learner should be able to add, subtract and multiply fractions in real life situations."},
                    {"name": "Determine reciprocals and divide fractions", "description": "By the end of the sub strand, the learner should be able to determine reciprocals of fractions and divide fractions."},
                    {"name": "Apply fractions in real life", "description": "By the end of the sub strand, the learner should be able to apply fractions in real life situations."},
                ]},
                {"name": "Decimals", "slos": [
                    {"name": "Identify place value of decimals", "description": "By the end of the sub strand, the learner should be able to identify the place value and total value of decimals."},
                    {"name": "Multiply and divide decimals", "description": "By the end of the sub strand, the learner should be able to multiply and divide decimals by whole numbers and decimals."},
                    {"name": "Apply decimals in real life", "description": "By the end of the sub strand, the learner should be able to recognize and use decimals in real life situations."},
                ]},
                {"name": "Squares and Square Roots", "slos": [
                    {"name": "Determine squares of numbers", "description": "By the end of the sub strand, the learner should be able to determine the squares of whole numbers, fractions and decimals."},
                    {"name": "Determine square roots of perfect squares", "description": "By the end of the sub strand, the learner should be able to determine the square roots of whole numbers, fractions and decimals of perfect squares."},
                    {"name": "Apply squares and square roots", "description": "By the end of the sub strand, the learner should be able to appreciate use of squares and square roots in real life situations."},
                ]},
            ]
        },
        {
            "name": "Algebra",
            "substrands": [
                {"name": "Algebraic Expressions", "slos": [
                    {"name": "Form algebraic expressions", "description": "By the end of the sub strand, the learner should be able to form algebraic expressions from real life situations."},
                    {"name": "Form expressions from algebraic statements", "description": "By the end of the sub strand, the learner should be able to form algebraic expressions from simple algebraic statements."},
                    {"name": "Simplify algebraic expressions", "description": "By the end of the sub strand, the learner should be able to simplify algebraic expressions in real life situations."},
                ]},
                {"name": "Linear Equations", "slos": [
                    {"name": "Form linear equations in one unknown", "description": "By the end of the sub strand, the learner should be able to form linear equations in one unknown from real life situations."},
                    {"name": "Solve linear equations in one unknown", "description": "By the end of the sub strand, the learner should be able to solve linear equations in one unknown."},
                    {"name": "Apply linear equations", "description": "By the end of the sub strand, the learner should be able to apply linear equations in solving problems in real life situations."},
                ]},
                {"name": "Linear Inequalities", "slos": [
                    {"name": "Form simple linear inequalities", "description": "By the end of the sub strand, the learner should be able to form simple linear inequalities in one unknown from real life situations."},
                    {"name": "Solve linear inequalities in one unknown", "description": "By the end of the sub strand, the learner should be able to solve linear inequalities in one unknown."},
                    {"name": "Represent solutions on number line", "description": "By the end of the sub strand, the learner should be able to represent solutions of inequalities on a number line."},
                ]},
            ]
        },
        {
            "name": "Measurements",
            "substrands": [
                {"name": "Length", "slos": [
                    {"name": "Convert units of length", "description": "By the end of the sub strand, the learner should be able to convert units of length from one form to another."},
                    {"name": "Calculate perimeter of plane figures", "description": "By the end of the sub strand, the learner should be able to calculate the perimeter of various plane figures."},
                    {"name": "Solve problems involving length", "description": "By the end of the sub strand, the learner should be able to solve problems involving length in real life situations."},
                ]},
                {"name": "Area", "slos": [
                    {"name": "Work out area of regular plane figures", "description": "By the end of the sub strand, the learner should be able to work out area of regular plane figures including triangles, rectangles, and parallelograms."},
                    {"name": "Calculate area of circles", "description": "By the end of the sub strand, the learner should be able to calculate the area of circles."},
                    {"name": "Calculate area of combined shapes", "description": "By the end of the sub strand, the learner should be able to calculate the area of combined shapes."},
                ]},
                {"name": "Volume and Capacity", "slos": [
                    {"name": "Calculate volume of cuboids", "description": "By the end of the sub strand, the learner should be able to calculate the volume of cuboids."},
                    {"name": "Calculate volume of cylinders", "description": "By the end of the sub strand, the learner should be able to calculate the volume of cylinders."},
                    {"name": "Convert units of volume and capacity", "description": "By the end of the sub strand, the learner should be able to convert units of volume and capacity."},
                ]},
                {"name": "Mass and Density", "slos": [
                    {"name": "Convert units of mass", "description": "By the end of the sub strand, the learner should be able to convert units of mass from one form to another."},
                    {"name": "Calculate density of substances", "description": "By the end of the sub strand, the learner should be able to calculate the density of substances."},
                    {"name": "Apply density in real life", "description": "By the end of the sub strand, the learner should be able to apply density in real life situations."},
                ]},
                {"name": "Time", "slos": [
                    {"name": "Work out time in 12-hour and 24-hour systems", "description": "By the end of the sub strand, the learner should be able to work out time using 12-hour and 24-hour systems."},
                    {"name": "Calculate travel time and speed", "description": "By the end of the sub strand, the learner should be able to calculate travel time, average speed and distance."},
                    {"name": "Apply time calculations in daily life", "description": "By the end of the sub strand, the learner should be able to apply time calculations in daily life situations."},
                ]},
                {"name": "Money", "slos": [
                    {"name": "Perform calculations involving money", "description": "By the end of the sub strand, the learner should be able to perform calculations involving money."},
                    {"name": "Calculate profit and loss", "description": "By the end of the sub strand, the learner should be able to calculate profit and loss."},
                    {"name": "Calculate simple interest", "description": "By the end of the sub strand, the learner should be able to calculate simple interest."},
                    {"name": "Prepare simple budgets", "description": "By the end of the sub strand, the learner should be able to prepare simple budgets."},
                ]},
            ]
        },
        {
            "name": "Geometry",
            "substrands": [
                {"name": "Lines and Angles", "slos": [
                    {"name": "Identify types of angles", "description": "By the end of the sub strand, the learner should be able to identify types of angles including acute, right, obtuse, straight and reflex angles."},
                    {"name": "Measure and construct angles", "description": "By the end of the sub strand, the learner should be able to measure and construct angles using protractors."},
                    {"name": "Calculate angle properties", "description": "By the end of the sub strand, the learner should be able to calculate angles on a straight line and angles at a point."},
                ]},
                {"name": "Plane Figures", "slos": [
                    {"name": "Identify properties of triangles", "description": "By the end of the sub strand, the learner should be able to identify and describe properties of triangles."},
                    {"name": "Identify properties of quadrilaterals", "description": "By the end of the sub strand, the learner should be able to identify and describe properties of quadrilaterals."},
                    {"name": "Construct plane figures", "description": "By the end of the sub strand, the learner should be able to construct various plane figures."},
                ]},
                {"name": "Circles", "slos": [
                    {"name": "Identify parts of a circle", "description": "By the end of the sub strand, the learner should be able to identify parts of a circle including radius, diameter, chord, arc and sector."},
                    {"name": "Calculate circumference", "description": "By the end of the sub strand, the learner should be able to calculate the circumference of a circle."},
                    {"name": "Construct circles and arcs", "description": "By the end of the sub strand, the learner should be able to construct circles and arcs using compass."},
                ]},
                {"name": "Geometrical Constructions", "slos": [
                    {"name": "Bisect lines and angles", "description": "By the end of the sub strand, the learner should be able to bisect lines and angles using a pair of compasses and ruler."},
                    {"name": "Construct perpendicular lines", "description": "By the end of the sub strand, the learner should be able to construct perpendicular lines."},
                    {"name": "Construct parallel lines", "description": "By the end of the sub strand, the learner should be able to construct parallel lines."},
                ]},
            ]
        },
        {
            "name": "Data Handling and Probability",
            "substrands": [
                {"name": "Data Collection and Organization", "slos": [
                    {"name": "Collect and organize data", "description": "By the end of the sub strand, the learner should be able to collect data using various methods including questionnaires and interviews."},
                    {"name": "Organize data in frequency tables", "description": "By the end of the sub strand, the learner should be able to organize data in frequency distribution tables."},
                    {"name": "Identify data sources", "description": "By the end of the sub strand, the learner should be able to identify primary and secondary sources of data."},
                ]},
                {"name": "Data Representation", "slos": [
                    {"name": "Represent data using pictographs", "description": "By the end of the sub strand, the learner should be able to represent data using pictographs and bar graphs."},
                    {"name": "Draw and interpret pie charts", "description": "By the end of the sub strand, the learner should be able to draw and interpret pie charts."},
                    {"name": "Draw and interpret line graphs", "description": "By the end of the sub strand, the learner should be able to draw and interpret line graphs."},
                ]},
                {"name": "Measures of Central Tendency", "slos": [
                    {"name": "Calculate mean of data", "description": "By the end of the sub strand, the learner should be able to calculate the mean of ungrouped data."},
                    {"name": "Determine mode and median", "description": "By the end of the sub strand, the learner should be able to determine the mode and median of ungrouped data."},
                    {"name": "Apply measures of central tendency", "description": "By the end of the sub strand, the learner should be able to apply measures of central tendency in real life situations."},
                ]},
                {"name": "Probability", "slos": [
                    {"name": "Define probability terms", "description": "By the end of the sub strand, the learner should be able to define probability and related terms."},
                    {"name": "Calculate probability of events", "description": "By the end of the sub strand, the learner should be able to calculate probability of simple events."},
                    {"name": "Apply probability in predictions", "description": "By the end of the sub strand, the learner should be able to apply probability in making predictions."},
                ]},
            ]
        },
    ]
    
    return strand_definitions


def parse_integrated_science_curriculum(text):
    """Parse Integrated Science curriculum"""
    return [
        {
            "name": "Scientific Investigation",
            "substrands": [
                {"name": "Introduction to Science", "slos": [
                    {"name": "Define science and its branches", "description": "By the end of the sub strand, the learner should be able to define science and identify its branches."},
                    {"name": "Explain importance of science", "description": "By the end of the sub strand, the learner should be able to explain the importance of science in daily life."},
                    {"name": "Identify scientific methods", "description": "By the end of the sub strand, the learner should be able to identify and apply scientific methods of investigation."},
                ]},
                {"name": "Laboratory Safety", "slos": [
                    {"name": "Identify laboratory equipment", "description": "By the end of the sub strand, the learner should be able to identify common laboratory equipment and their uses."},
                    {"name": "Follow laboratory safety rules", "description": "By the end of the sub strand, the learner should be able to follow laboratory safety rules and procedures."},
                    {"name": "Handle chemicals safely", "description": "By the end of the sub strand, the learner should be able to handle chemicals and equipment safely."},
                ]},
            ]
        },
        {
            "name": "Living Things and Their Environment",
            "substrands": [
                {"name": "Classification of Living Things", "slos": [
                    {"name": "Classify living things", "description": "By the end of the sub strand, the learner should be able to classify living things into major groups."},
                    {"name": "Identify characteristics of living things", "description": "By the end of the sub strand, the learner should be able to identify characteristics of living things."},
                    {"name": "Use classification keys", "description": "By the end of the sub strand, the learner should be able to use simple classification keys to identify organisms."},
                ]},
                {"name": "Cell Structure", "slos": [
                    {"name": "Describe the cell as unit of life", "description": "By the end of the sub strand, the learner should be able to describe the cell as the basic unit of life."},
                    {"name": "Identify parts of a cell", "description": "By the end of the sub strand, the learner should be able to identify parts of plant and animal cells."},
                    {"name": "Compare plant and animal cells", "description": "By the end of the sub strand, the learner should be able to compare plant and animal cells."},
                ]},
                {"name": "Human Body Systems", "slos": [
                    {"name": "Describe the digestive system", "description": "By the end of the sub strand, the learner should be able to describe the structure and function of the digestive system."},
                    {"name": "Describe the respiratory system", "description": "By the end of the sub strand, the learner should be able to describe the structure and function of the respiratory system."},
                    {"name": "Describe the circulatory system", "description": "By the end of the sub strand, the learner should be able to describe the structure and function of the circulatory system."},
                    {"name": "Explain maintaining healthy body systems", "description": "By the end of the sub strand, the learner should be able to explain ways of maintaining healthy body systems."},
                ]},
                {"name": "Ecosystems", "slos": [
                    {"name": "Define ecosystem components", "description": "By the end of the sub strand, the learner should be able to define ecosystem and identify its components."},
                    {"name": "Describe food chains and webs", "description": "By the end of the sub strand, the learner should be able to describe food chains and food webs."},
                    {"name": "Explain nutrient cycling", "description": "By the end of the sub strand, the learner should be able to explain nutrient cycling in ecosystems."},
                    {"name": "Discuss environmental conservation", "description": "By the end of the sub strand, the learner should be able to discuss importance of environmental conservation."},
                ]},
            ]
        },
        {
            "name": "Matter and Materials",
            "substrands": [
                {"name": "States of Matter", "slos": [
                    {"name": "Identify states of matter", "description": "By the end of the sub strand, the learner should be able to identify the three states of matter."},
                    {"name": "Describe properties of states of matter", "description": "By the end of the sub strand, the learner should be able to describe properties of solids, liquids and gases."},
                    {"name": "Explain changes of state", "description": "By the end of the sub strand, the learner should be able to explain changes of state and factors affecting them."},
                ]},
                {"name": "Mixtures and Pure Substances", "slos": [
                    {"name": "Distinguish mixtures from pure substances", "description": "By the end of the sub strand, the learner should be able to distinguish between mixtures and pure substances."},
                    {"name": "Classify mixtures", "description": "By the end of the sub strand, the learner should be able to classify mixtures as homogeneous or heterogeneous."},
                    {"name": "Separate mixtures", "description": "By the end of the sub strand, the learner should be able to separate components of mixtures using various methods."},
                ]},
                {"name": "Elements and Compounds", "slos": [
                    {"name": "Define elements and compounds", "description": "By the end of the sub strand, the learner should be able to define elements and compounds."},
                    {"name": "Identify common elements", "description": "By the end of the sub strand, the learner should be able to identify common elements and their symbols."},
                    {"name": "Write chemical formulae", "description": "By the end of the sub strand, the learner should be able to write simple chemical formulae."},
                ]},
                {"name": "Acids and Bases", "slos": [
                    {"name": "Identify acids and bases", "description": "By the end of the sub strand, the learner should be able to identify acids and bases using indicators."},
                    {"name": "Describe properties of acids and bases", "description": "By the end of the sub strand, the learner should be able to describe properties of acids and bases."},
                    {"name": "Apply pH scale", "description": "By the end of the sub strand, the learner should be able to apply pH scale to measure acidity and alkalinity."},
                ]},
            ]
        },
        {
            "name": "Energy, Forces and Motion",
            "substrands": [
                {"name": "Forms of Energy", "slos": [
                    {"name": "Identify forms of energy", "description": "By the end of the sub strand, the learner should be able to identify different forms of energy."},
                    {"name": "Describe energy transformations", "description": "By the end of the sub strand, the learner should be able to describe energy transformations."},
                    {"name": "Apply law of conservation of energy", "description": "By the end of the sub strand, the learner should be able to apply the law of conservation of energy."},
                ]},
                {"name": "Heat Energy", "slos": [
                    {"name": "Describe heat transfer methods", "description": "By the end of the sub strand, the learner should be able to describe conduction, convection and radiation."},
                    {"name": "Investigate factors affecting heat transfer", "description": "By the end of the sub strand, the learner should be able to investigate factors affecting heat transfer."},
                    {"name": "Apply heat transfer in daily life", "description": "By the end of the sub strand, the learner should be able to apply knowledge of heat transfer in daily life."},
                ]},
                {"name": "Light Energy", "slos": [
                    {"name": "Describe properties of light", "description": "By the end of the sub strand, the learner should be able to describe properties of light."},
                    {"name": "Explain reflection and refraction", "description": "By the end of the sub strand, the learner should be able to explain reflection and refraction of light."},
                    {"name": "Describe formation of images", "description": "By the end of the sub strand, the learner should be able to describe formation of images by mirrors and lenses."},
                ]},
                {"name": "Sound Energy", "slos": [
                    {"name": "Describe how sound is produced", "description": "By the end of the sub strand, the learner should be able to describe how sound is produced and transmitted."},
                    {"name": "Identify properties of sound", "description": "By the end of the sub strand, the learner should be able to identify properties of sound including pitch and loudness."},
                    {"name": "Discuss noise pollution", "description": "By the end of the sub strand, the learner should be able to discuss causes and effects of noise pollution."},
                ]},
                {"name": "Electrical Energy", "slos": [
                    {"name": "Describe sources of electricity", "description": "By the end of the sub strand, the learner should be able to describe sources of electricity."},
                    {"name": "Construct simple circuits", "description": "By the end of the sub strand, the learner should be able to construct simple electric circuits."},
                    {"name": "Practice electrical safety", "description": "By the end of the sub strand, the learner should be able to practice electrical safety measures."},
                ]},
                {"name": "Forces and Motion", "slos": [
                    {"name": "Define force and its effects", "description": "By the end of the sub strand, the learner should be able to define force and describe its effects."},
                    {"name": "Identify types of forces", "description": "By the end of the sub strand, the learner should be able to identify different types of forces."},
                    {"name": "Calculate speed and velocity", "description": "By the end of the sub strand, the learner should be able to calculate speed and velocity."},
                ]},
            ]
        },
        {
            "name": "Earth and Space",
            "substrands": [
                {"name": "The Solar System", "slos": [
                    {"name": "Describe components of solar system", "description": "By the end of the sub strand, the learner should be able to describe the sun, planets and other bodies in the solar system."},
                    {"name": "Explain Earth's movements", "description": "By the end of the sub strand, the learner should be able to explain rotation and revolution of the Earth."},
                    {"name": "Describe phases of the moon", "description": "By the end of the sub strand, the learner should be able to describe phases of the moon and eclipses."},
                ]},
                {"name": "Weather and Climate", "slos": [
                    {"name": "Distinguish weather from climate", "description": "By the end of the sub strand, the learner should be able to distinguish between weather and climate."},
                    {"name": "Identify elements of weather", "description": "By the end of the sub strand, the learner should be able to identify and measure elements of weather."},
                    {"name": "Discuss climate change", "description": "By the end of the sub strand, the learner should be able to discuss causes and effects of climate change."},
                ]},
                {"name": "Rocks and Soil", "slos": [
                    {"name": "Classify types of rocks", "description": "By the end of the sub strand, the learner should be able to classify rocks as igneous, sedimentary and metamorphic."},
                    {"name": "Describe rock cycle", "description": "By the end of the sub strand, the learner should be able to describe the rock cycle."},
                    {"name": "Explain soil formation", "description": "By the end of the sub strand, the learner should be able to explain soil formation and types of soil."},
                ]},
            ]
        },
    ]


def parse_social_studies_curriculum(text):
    """Parse Social Studies curriculum"""
    return [
        {
            "name": "Environment and Resources",
            "substrands": [
                {"name": "Physical Features of Kenya", "slos": [
                    {"name": "Identify major physical features", "description": "By the end of the sub strand, the learner should be able to identify major physical features of Kenya."},
                    {"name": "Describe formation of physical features", "description": "By the end of the sub strand, the learner should be able to describe how physical features were formed."},
                    {"name": "Explain significance of physical features", "description": "By the end of the sub strand, the learner should be able to explain significance of physical features to human activities."},
                ]},
                {"name": "Climate of Kenya", "slos": [
                    {"name": "Describe climate regions", "description": "By the end of the sub strand, the learner should be able to describe climate regions of Kenya."},
                    {"name": "Explain factors influencing climate", "description": "By the end of the sub strand, the learner should be able to explain factors influencing climate in Kenya."},
                    {"name": "Analyze effects of climate on activities", "description": "By the end of the sub strand, the learner should be able to analyze effects of climate on human activities."},
                ]},
                {"name": "Natural Resources", "slos": [
                    {"name": "Identify natural resources in Kenya", "description": "By the end of the sub strand, the learner should be able to identify natural resources in Kenya."},
                    {"name": "Classify renewable and non-renewable resources", "description": "By the end of the sub strand, the learner should be able to classify natural resources as renewable and non-renewable."},
                    {"name": "Discuss conservation of resources", "description": "By the end of the sub strand, the learner should be able to discuss ways of conserving natural resources."},
                ]},
            ]
        },
        {
            "name": "Population and Settlement",
            "substrands": [
                {"name": "Population Distribution", "slos": [
                    {"name": "Describe population distribution in Kenya", "description": "By the end of the sub strand, the learner should be able to describe population distribution in Kenya."},
                    {"name": "Explain factors affecting distribution", "description": "By the end of the sub strand, the learner should be able to explain factors affecting population distribution."},
                    {"name": "Analyze population data", "description": "By the end of the sub strand, the learner should be able to analyze population data from various sources."},
                ]},
                {"name": "Migration", "slos": [
                    {"name": "Define types of migration", "description": "By the end of the sub strand, the learner should be able to define and classify types of migration."},
                    {"name": "Explain causes of migration", "description": "By the end of the sub strand, the learner should be able to explain causes of rural-urban migration."},
                    {"name": "Discuss effects of migration", "description": "By the end of the sub strand, the learner should be able to discuss effects of migration."},
                ]},
                {"name": "Settlement Patterns", "slos": [
                    {"name": "Identify settlement patterns", "description": "By the end of the sub strand, the learner should be able to identify different settlement patterns in Kenya."},
                    {"name": "Compare rural and urban settlements", "description": "By the end of the sub strand, the learner should be able to compare rural and urban settlements."},
                    {"name": "Discuss urbanization challenges", "description": "By the end of the sub strand, the learner should be able to discuss challenges of urbanization."},
                ]},
            ]
        },
        {
            "name": "History and Government",
            "substrands": [
                {"name": "Early Societies in Kenya", "slos": [
                    {"name": "Describe early human societies", "description": "By the end of the sub strand, the learner should be able to describe early human societies in Kenya."},
                    {"name": "Explain migration and settlement", "description": "By the end of the sub strand, the learner should be able to explain migration and settlement of communities."},
                    {"name": "Discuss social organization", "description": "By the end of the sub strand, the learner should be able to discuss social organization of early communities."},
                ]},
                {"name": "Colonial Period", "slos": [
                    {"name": "Explain establishment of colonial rule", "description": "By the end of the sub strand, the learner should be able to explain establishment of colonial rule in Kenya."},
                    {"name": "Describe effects of colonialism", "description": "By the end of the sub strand, the learner should be able to describe social, economic and political effects of colonialism."},
                    {"name": "Discuss African resistance", "description": "By the end of the sub strand, the learner should be able to discuss African resistance to colonial rule."},
                ]},
                {"name": "Independent Kenya", "slos": [
                    {"name": "Describe attainment of independence", "description": "By the end of the sub strand, the learner should be able to describe the struggle for and attainment of independence."},
                    {"name": "Explain political developments", "description": "By the end of the sub strand, the learner should be able to explain major political developments since independence."},
                    {"name": "Identify national heroes", "description": "By the end of the sub strand, the learner should be able to identify and appreciate national heroes and heroines."},
                ]},
                {"name": "Government of Kenya", "slos": [
                    {"name": "Describe structure of government", "description": "By the end of the sub strand, the learner should be able to describe the structure of Kenya government."},
                    {"name": "Explain devolution", "description": "By the end of the sub strand, the learner should be able to explain devolution and county governments."},
                    {"name": "Discuss citizen participation", "description": "By the end of the sub strand, the learner should be able to discuss ways of citizen participation in governance."},
                ]},
            ]
        },
        {
            "name": "Economic Activities",
            "substrands": [
                {"name": "Agriculture", "slos": [
                    {"name": "Describe types of farming", "description": "By the end of the sub strand, the learner should be able to describe types of farming practiced in Kenya."},
                    {"name": "Explain factors affecting agriculture", "description": "By the end of the sub strand, the learner should be able to explain factors affecting agriculture."},
                    {"name": "Discuss contribution to economy", "description": "By the end of the sub strand, the learner should be able to discuss contribution of agriculture to the economy."},
                ]},
                {"name": "Trade and Industry", "slos": [
                    {"name": "Define types of trade", "description": "By the end of the sub strand, the learner should be able to define and classify types of trade."},
                    {"name": "Describe Kenya's trade relations", "description": "By the end of the sub strand, the learner should be able to describe Kenya's trade relations."},
                    {"name": "Discuss industrialization", "description": "By the end of the sub strand, the learner should be able to discuss industrialization in Kenya."},
                ]},
                {"name": "Transport and Communication", "slos": [
                    {"name": "Identify modes of transport", "description": "By the end of the sub strand, the learner should be able to identify modes of transport in Kenya."},
                    {"name": "Explain importance of transport", "description": "By the end of the sub strand, the learner should be able to explain importance of transport to economic development."},
                    {"name": "Describe communication systems", "description": "By the end of the sub strand, the learner should be able to describe communication systems in Kenya."},
                ]},
                {"name": "Tourism", "slos": [
                    {"name": "Identify tourist attractions", "description": "By the end of the sub strand, the learner should be able to identify major tourist attractions in Kenya."},
                    {"name": "Explain factors promoting tourism", "description": "By the end of the sub strand, the learner should be able to explain factors promoting tourism."},
                    {"name": "Discuss contribution of tourism", "description": "By the end of the sub strand, the learner should be able to discuss contribution of tourism to the economy."},
                ]},
            ]
        },
        {
            "name": "Citizenship and Values",
            "substrands": [
                {"name": "Rights and Responsibilities", "slos": [
                    {"name": "Identify rights of citizens", "description": "By the end of the sub strand, the learner should be able to identify rights of citizens in the constitution."},
                    {"name": "Explain responsibilities of citizens", "description": "By the end of the sub strand, the learner should be able to explain responsibilities of citizens."},
                    {"name": "Demonstrate responsible citizenship", "description": "By the end of the sub strand, the learner should be able to demonstrate responsible citizenship."},
                ]},
                {"name": "National Unity", "slos": [
                    {"name": "Identify national symbols", "description": "By the end of the sub strand, the learner should be able to identify national symbols and their significance."},
                    {"name": "Explain importance of national unity", "description": "By the end of the sub strand, the learner should be able to explain importance of national unity."},
                    {"name": "Participate in unity activities", "description": "By the end of the sub strand, the learner should be able to participate in activities promoting national unity."},
                ]},
            ]
        },
    ]


async def clear_existing_subject_data(subject_name):
    """Clear existing strands, substrands, and SLOs for a subject"""
    subject = await db.subjects.find_one({"name": subject_name})
    if not subject:
        return
    
    subject_id = subject.get('id', str(subject['_id']))
    
    # Get all strands for this subject
    strands = await db.strands.find({"subjectId": subject_id}).to_list(None)
    
    for strand in strands:
        strand_id = strand.get('id', str(strand['_id']))
        
        # Get all substrands for this strand
        substrands = await db.substrands.find({"strandId": strand_id}).to_list(None)
        
        for substrand in substrands:
            substrand_id = substrand.get('id', str(substrand['_id']))
            # Delete all SLOs for this substrand
            await db.slos.delete_many({"substrandId": substrand_id})
        
        # Delete all substrands for this strand
        await db.substrands.delete_many({"strandId": strand_id})
    
    # Delete all strands for this subject
    await db.strands.delete_many({"subjectId": subject_id})
    
    print(f"  Cleared existing data for {subject_name}")


async def seed_subject_from_parsed_data(subject_name, parsed_data, grade_ids):
    """Seed a subject with parsed curriculum data"""
    print(f"\n--- Seeding {subject_name} from PDF ---")
    
    # Clear existing data first
    await clear_existing_subject_data(subject_name)
    
    # Get or create subject
    subject = await db.subjects.find_one({"name": subject_name})
    if subject:
        subject_id = subject.get('id', str(subject['_id']))
        # Update grade IDs
        await db.subjects.update_one(
            {"name": subject_name},
            {"$addToSet": {"gradeIds": {"$each": grade_ids}}}
        )
    else:
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
    
    for strand_data in parsed_data:
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
    """Main function to parse PDFs and seed database"""
    print("=" * 70)
    print("PARSING KICD CURRICULUM PDFs AND SEEDING DATABASE")
    print("=" * 70)
    
    # Get grade IDs for Junior Secondary
    grade_7 = await db.grades.find_one({"name": "Grade 7"})
    grade_8 = await db.grades.find_one({"name": "Grade 8"})
    grade_9 = await db.grades.find_one({"name": "Grade 9"})
    
    if not all([grade_7, grade_8, grade_9]):
        print("ERROR: Grades 7, 8, 9 not found in database. Run seed_subjects.py first.")
        return
    
    grade_ids = [
        grade_7.get('id', str(grade_7['_id'])),
        grade_8.get('id', str(grade_8['_id'])),
        grade_9.get('id', str(grade_9['_id']))
    ]
    
    print(f"Grade IDs: 7={grade_ids[0][:8]}..., 8={grade_ids[1][:8]}..., 9={grade_ids[2][:8]}...")
    
    total_strands = 0
    total_substrands = 0
    total_slos = 0
    
    # Parse and seed Mathematics
    math_text = extract_text_from_pdf('/app/backend/pdfs/grade7_rationalized/mathematics.pdf')
    math_data = parse_mathematics_curriculum(math_text)
    s, ss, slo = await seed_subject_from_parsed_data("Mathematics", math_data, grade_ids)
    total_strands += s
    total_substrands += ss
    total_slos += slo
    
    # Parse and seed Integrated Science
    science_text = extract_text_from_pdf('/app/backend/pdfs/grade7_rationalized/integrated_science.pdf')
    science_data = parse_integrated_science_curriculum(science_text)
    s, ss, slo = await seed_subject_from_parsed_data("Integrated Science", science_data, grade_ids)
    total_strands += s
    total_substrands += ss
    total_slos += slo
    
    # Parse and seed Social Studies
    social_text = extract_text_from_pdf('/app/backend/pdfs/grade7_rationalized/social_studies.pdf')
    social_data = parse_social_studies_curriculum(social_text)
    s, ss, slo = await seed_subject_from_parsed_data("Social Studies", social_data, grade_ids)
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
