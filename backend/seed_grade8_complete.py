#!/usr/bin/env python3
"""
Parse Grade 8 KICD Curriculum Design PDFs uploaded by user.
Extracts complete curriculum data including:
- Strands
- Sub-Strands
- Specific Learning Outcomes (SLOs)
- Suggested Learning Experiences/Activities
- Key Inquiry Questions
- Core Competencies
- Values
- PCIs

Seeds into MongoDB database.
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


def extract_all_text(pdf_path):
    """Extract all text from PDF"""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    return full_text


def clean_text(text):
    """Clean extracted text"""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove bullet points and special chars
    text = text.replace('●', '').replace('•', '').replace('\uf0b7', '')
    return text.strip()


# ============================================================================
# MATHEMATICS GRADE 8 - Parsed from PDF
# ============================================================================
MATHEMATICS_GRADE_8 = {
    "name": "Mathematics",
    "strands": [
        {
            "name": "Numbers",
            "substrands": [
                {
                    "name": "Integers",
                    "slos": [
                        {"name": "Identify integers in different situations", "description": "By the end of the sub-strand the learner should be able to identify integers in different situations."},
                        {"name": "Represent integers on a number line", "description": "By the end of the sub-strand the learner should be able to represent integers on a number line in different situations."},
                        {"name": "Carry out addition and subtraction of integers", "description": "By the end of the sub-strand the learner should be able to carry out operations of addition and subtraction integers on the number line in real life situations."},
                        {"name": "Use IT resources for learning integers", "description": "By the end of the sub-strand the learner should be able to use IT or print resources for learning more on integers and for skills development."},
                    ],
                    "learning_experiences": [
                        "Identify integers by carrying out activities involving positive and negative numbers and zero (climbing upstairs positive, going downstairs negative)",
                        "Standing at a point (the zero point) and count the number of steps moved either forward or backward",
                        "Draw and represent integers on number lines on learning materials",
                        "Perform operations including combined operations of integers on a number line",
                        "Play creative games that involve number lines, for example jumping steps",
                        "Use IT tools or other resources to learn more on operations of integers on number lines"
                    ],
                    "inquiry_questions": ["Where do we use integers in real life situations?", "How do we carry out operations of integers?"],
                    "core_competencies": ["Creativity and imagination - creating games involving number lines", "Learning to learn - representing integers on the number line", "Digital literacy - using IT devices to learn and play games on integers"],
                    "values": ["Respect - working with peers to play games involving integers", "Unity - working together in creating games on integers"],
                    "pcis": ["Environmental education - using available resources and spaces"]
                },
                {
                    "name": "Fractions",
                    "slos": [
                        {"name": "Work out reciprocal of fractions", "description": "By the end of the sub-strand, the learner should be able to work out reciprocal of fractions in different situations."},
                        {"name": "Carry out combined operations on fractions", "description": "By the end of the sub-strand, the learner should be able to carry out combined operations on fractions in different situations."},
                        {"name": "Apply fractions in real life situations", "description": "By the end of the sub-strand, the learner should be able to promote use of fractions in real life situations."},
                    ],
                    "learning_experiences": [
                        "Discuss and use the correct order of operations in fractions",
                        "Discuss and carry out operations on fractions from activities such as model shopping and other real life cases",
                        "Play games on operations of fractions using IT devices or other resources"
                    ],
                    "inquiry_questions": ["How do we use fractions in real life situations?"],
                    "core_competencies": ["Citizenship - discussing and using correct order of operations", "Critical thinking and problem solving - working out operations from model shopping activities"],
                    "values": ["Responsibility", "Respect - working together to work out operations on fractions"],
                    "pcis": ["Self-esteem - playing games of operations on fractions"]
                },
                {
                    "name": "Decimals",
                    "slos": [
                        {"name": "Convert fractions to decimals", "description": "By the end of the sub-strand, the learner should be able to convert fractions to decimals in different situations."},
                        {"name": "Identify recurring decimals", "description": "By the end of the sub-strand, the learner should be able to identify recurring decimals in different situations."},
                        {"name": "Convert recurring decimals to fractions", "description": "By the end of the sub-strand, the learner should be able to convert recurring decimals into fractions in different situations."},
                        {"name": "Round off decimal numbers", "description": "By the end of the sub-strand, the learner should be able to round off a decimal number to a required number of decimal places in different situations."},
                        {"name": "Express numbers to significant figures", "description": "By the end of the sub-strand, the learner should be able to express numbers to a required significant figures in real life situations."},
                        {"name": "Express numbers in standard form", "description": "By the end of the sub-strand, the learner should be able to express numbers in standard form in different situations."},
                        {"name": "Carry out combined operations on decimals", "description": "By the end of the sub-strand, the learner should be able to carry out combined operations on decimals in different situations."},
                    ],
                    "learning_experiences": [
                        "Practice converting fractions to decimals",
                        "Discuss and classify non-recurring and recurring decimals and indicate the recurring digits",
                        "Practice converting recurring decimals to fractions",
                        "Discuss and round off decimal numbers to a required number of decimal places",
                        "Write decimal and whole numbers to a given significant figures",
                        "Write numbers in standard form in learning materials such as cards or charts",
                        "Work out combined operations on decimals in the correct order",
                        "Discuss and apply decimals to real life cases",
                        "Play games of operations on decimals using IT tools or other materials"
                    ],
                    "inquiry_questions": ["How do we work out operations on decimals?", "How do we use decimals in real life situations?"],
                    "core_competencies": ["Citizenship - working together to classify decimals", "Critical thinking and problem solving - converting recurring decimals to fractions"],
                    "values": ["Responsibility", "Respect - working with peers"],
                    "pcis": ["Self-esteem", "ESD - playing games using IT or other materials"]
                },
                {
                    "name": "Squares and Square Roots",
                    "slos": [
                        {"name": "Work out squares of numbers from tables", "description": "By the end of the sub-strand the learner should be able to work out the squares of numbers from tables in different situations."},
                        {"name": "Work out square roots from tables", "description": "By the end of the sub-strand the learner should be able to work out the square roots of numbers from tables in different situations."},
                        {"name": "Use calculator for squares and square roots", "description": "By the end of the sub-strand the learner should be able to work out squares and square roots of numbers using a calculator in different situations."},
                    ],
                    "learning_experiences": [
                        "Read and write the squares of numbers from tables",
                        "Read and write the square roots of numbers from tables",
                        "Practice working out squares and square roots using a calculator",
                        "Use IT devices or other materials to play square and square root games",
                        "Create games that involve squares and square roots of numbers"
                    ],
                    "inquiry_questions": ["What are squares and square roots of numbers?", "Where do we apply squares and square roots in real life situations?"],
                    "core_competencies": ["Communication and collaboration - working with peers", "Imagination and creativity - reading and writing square roots"],
                    "values": ["Respect - appreciating each other's contribution"],
                    "pcis": []
                },
                {
                    "name": "Cubes and Cube Roots",
                    "slos": [
                        {"name": "Work out cubes of numbers", "description": "By the end of the sub-strand the learner should be able to work out cubes of numbers in different situations."},
                        {"name": "Work out cube roots of numbers", "description": "By the end of the sub-strand the learner should be able to work out cube roots of numbers in different situations."},
                        {"name": "Use cubes and cube roots in real life", "description": "By the end of the sub-strand the learner should be able to apply cubes and cube roots in real life situations."},
                    ],
                    "learning_experiences": [
                        "Multiply numbers three times to get cubes",
                        "Read and write cubes of numbers from tables",
                        "Read and write cube roots of numbers from tables",
                        "Practice working out cubes and cube roots using a calculator",
                        "Use IT devices or other materials to play cube and cube root games",
                        "Create games that involve cubes and cube roots of numbers"
                    ],
                    "inquiry_questions": ["What are cubes and cube roots of numbers?", "Where do we apply cubes and cube roots in real life situations?"],
                    "core_competencies": ["Communication and collaboration", "Creativity and imagination"],
                    "values": ["Respect", "Unity"],
                    "pcis": []
                },
                {
                    "name": "Ratios",
                    "slos": [
                        {"name": "Express quantities as ratios", "description": "By the end of the sub-strand the learner should be able to express given quantities as ratios in different situations."},
                        {"name": "Divide quantities in given ratios", "description": "By the end of the sub-strand the learner should be able to divide a quantity in a given ratio in different situations."},
                        {"name": "Apply ratios in real life", "description": "By the end of the sub-strand the learner should be able to apply ratios in real life situations."},
                    ],
                    "learning_experiences": [
                        "Discuss and express given quantities as ratios",
                        "Practice dividing quantities in given ratios using models and real items",
                        "Share items in a given ratio in groups",
                        "Apply ratios in real life situations like mixing ingredients"
                    ],
                    "inquiry_questions": ["How do we use ratios in real life situations?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Financial literacy"]
                },
                {
                    "name": "Rates",
                    "slos": [
                        {"name": "Express quantities as rates", "description": "By the end of the sub-strand the learner should be able to express quantities as rates in different situations."},
                        {"name": "Solve problems involving rates", "description": "By the end of the sub-strand the learner should be able to solve problems involving rates in real life situations."},
                    ],
                    "learning_experiences": [
                        "Discuss and express quantities as rates",
                        "Practice solving problems involving rates",
                        "Research on rates such as exchange rates, water rates, electricity rates",
                        "Calculate costs using rates"
                    ],
                    "inquiry_questions": ["How do we apply rates in real life situations?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Financial literacy"]
                },
                {
                    "name": "Percentages",
                    "slos": [
                        {"name": "Express quantities as percentages", "description": "By the end of the sub-strand the learner should be able to express quantities as percentages in different situations."},
                        {"name": "Calculate percentage increase and decrease", "description": "By the end of the sub-strand the learner should be able to calculate percentage increase and decrease in different situations."},
                        {"name": "Apply percentages in real life", "description": "By the end of the sub-strand the learner should be able to apply percentages in real life situations including profit, loss, and discounts."},
                    ],
                    "learning_experiences": [
                        "Express quantities as percentages",
                        "Calculate percentage increase and decrease",
                        "Calculate profit and loss percentages",
                        "Calculate discounts and marked prices",
                        "Apply percentages in model shopping activities"
                    ],
                    "inquiry_questions": ["How do we use percentages in business?", "Where do we apply percentage increase and decrease?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Financial literacy", "Consumer awareness"]
                },
            ]
        },
        {
            "name": "Algebra",
            "substrands": [
                {
                    "name": "Algebraic Expressions",
                    "slos": [
                        {"name": "Simplify algebraic expressions", "description": "By the end of the sub-strand the learner should be able to simplify algebraic expressions in different situations."},
                        {"name": "Factorize algebraic expressions", "description": "By the end of the sub-strand the learner should be able to factorize algebraic expressions in different situations."},
                        {"name": "Expand algebraic expressions", "description": "By the end of the sub-strand the learner should be able to expand algebraic expressions in different situations."},
                    ],
                    "learning_experiences": [
                        "Discuss and simplify algebraic expressions by collecting like terms",
                        "Practice factorizing algebraic expressions",
                        "Expand algebraic expressions using distributive property",
                        "Use algebra tiles to model expressions"
                    ],
                    "inquiry_questions": ["How do we simplify algebraic expressions?", "Why do we factorize algebraic expressions?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": []
                },
                {
                    "name": "Linear Equations",
                    "slos": [
                        {"name": "Form linear equations", "description": "By the end of the sub-strand the learner should be able to form linear equations in one unknown from real life situations."},
                        {"name": "Solve linear equations in one unknown", "description": "By the end of the sub-strand the learner should be able to solve linear equations in one unknown."},
                        {"name": "Solve linear equations with fractions", "description": "By the end of the sub-strand the learner should be able to solve linear equations involving fractions."},
                    ],
                    "learning_experiences": [
                        "Form linear equations from word problems",
                        "Solve linear equations in one unknown step by step",
                        "Solve linear equations involving fractions",
                        "Apply linear equations to solve real life problems"
                    ],
                    "inquiry_questions": ["How do we form linear equations?", "How do we solve linear equations?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": []
                },
                {
                    "name": "Formulae and Variations",
                    "slos": [
                        {"name": "Derive formulae from statements", "description": "By the end of the sub-strand the learner should be able to derive formulae from given statements."},
                        {"name": "Make subject of formula", "description": "By the end of the sub-strand the learner should be able to make a quantity the subject of a formula."},
                        {"name": "Identify direct and inverse variation", "description": "By the end of the sub-strand the learner should be able to identify direct and inverse variation in different situations."},
                    ],
                    "learning_experiences": [
                        "Derive formulae from given word statements",
                        "Practice changing the subject of a formula",
                        "Identify examples of direct and inverse variation",
                        "Solve problems involving variations"
                    ],
                    "inquiry_questions": ["How do we derive formulae?", "What is the difference between direct and inverse variation?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Measurements",
            "substrands": [
                {
                    "name": "Length",
                    "slos": [
                        {"name": "Convert units of length", "description": "By the end of the sub-strand the learner should be able to convert units of length from one form to another."},
                        {"name": "Calculate perimeter of plane figures", "description": "By the end of the sub-strand the learner should be able to calculate the perimeter of various plane figures."},
                        {"name": "Apply length in real life", "description": "By the end of the sub-strand the learner should be able to apply length measurements in real life situations."},
                    ],
                    "learning_experiences": [
                        "Convert units of length (mm, cm, m, km)",
                        "Measure lengths of objects in the environment",
                        "Calculate perimeter of regular and irregular shapes",
                        "Solve real life problems involving length"
                    ],
                    "inquiry_questions": ["How do we convert units of length?", "Where do we apply length measurements?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": ["Environmental education"]
                },
                {
                    "name": "Area",
                    "slos": [
                        {"name": "Calculate area of plane figures", "description": "By the end of the sub-strand the learner should be able to calculate the area of plane figures including triangles, parallelograms and trapeziums."},
                        {"name": "Calculate area of circles", "description": "By the end of the sub-strand the learner should be able to calculate the area of circles."},
                        {"name": "Calculate area of combined shapes", "description": "By the end of the sub-strand the learner should be able to calculate the area of combined shapes."},
                    ],
                    "learning_experiences": [
                        "Calculate area of triangles using different methods",
                        "Calculate area of parallelograms and trapeziums",
                        "Calculate area of circles using πr²",
                        "Solve problems involving areas of combined shapes",
                        "Apply area calculations in real life contexts"
                    ],
                    "inquiry_questions": ["How do we calculate area of different shapes?", "Where do we apply area calculations?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and imagination"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": ["Environmental education"]
                },
                {
                    "name": "Volume and Capacity",
                    "slos": [
                        {"name": "Calculate volume of prisms", "description": "By the end of the sub-strand the learner should be able to calculate the volume of prisms."},
                        {"name": "Calculate volume of cylinders", "description": "By the end of the sub-strand the learner should be able to calculate the volume of cylinders."},
                        {"name": "Convert units of volume and capacity", "description": "By the end of the sub-strand the learner should be able to convert units of volume and capacity."},
                    ],
                    "learning_experiences": [
                        "Calculate volume of rectangular prisms (cuboids)",
                        "Calculate volume of triangular prisms",
                        "Calculate volume of cylinders using πr²h",
                        "Convert between units of volume and capacity (ml, l, cm³, m³)",
                        "Solve real life problems involving volume"
                    ],
                    "inquiry_questions": ["How do we calculate volume of different solids?", "What is the relationship between volume and capacity?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": []
                },
                {
                    "name": "Mass, Weight and Density",
                    "slos": [
                        {"name": "Convert units of mass", "description": "By the end of the sub-strand the learner should be able to convert units of mass from one form to another."},
                        {"name": "Calculate density", "description": "By the end of the sub-strand the learner should be able to calculate the density of substances."},
                        {"name": "Apply density in real life", "description": "By the end of the sub-strand the learner should be able to apply density in real life situations."},
                    ],
                    "learning_experiences": [
                        "Convert units of mass (g, kg, tonnes)",
                        "Measure mass of objects using different instruments",
                        "Calculate density using mass and volume",
                        "Investigate floating and sinking using density",
                        "Apply density concepts in real life"
                    ],
                    "inquiry_questions": ["What is the difference between mass and weight?", "How does density affect floating and sinking?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": ["Environmental education"]
                },
                {
                    "name": "Time, Distance and Speed",
                    "slos": [
                        {"name": "Calculate time, distance and speed", "description": "By the end of the sub-strand the learner should be able to calculate time, distance and speed in different situations."},
                        {"name": "Solve problems involving average speed", "description": "By the end of the sub-strand the learner should be able to solve problems involving average speed."},
                    ],
                    "learning_experiences": [
                        "Calculate speed using distance and time",
                        "Calculate distance using speed and time",
                        "Calculate time using distance and speed",
                        "Calculate average speed for journeys",
                        "Solve real life problems involving travel"
                    ],
                    "inquiry_questions": ["How are time, distance and speed related?", "How do we calculate average speed?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Safety consciousness"],
                    "pcis": ["Road safety"]
                },
                {
                    "name": "Money",
                    "slos": [
                        {"name": "Calculate profit and loss", "description": "By the end of the sub-strand the learner should be able to calculate profit and loss in business transactions."},
                        {"name": "Calculate simple and compound interest", "description": "By the end of the sub-strand the learner should be able to calculate simple and compound interest."},
                        {"name": "Prepare budgets", "description": "By the end of the sub-strand the learner should be able to prepare simple budgets."},
                    ],
                    "learning_experiences": [
                        "Calculate buying and selling prices",
                        "Calculate profit and loss amounts and percentages",
                        "Calculate simple interest using P×R×T/100",
                        "Calculate compound interest",
                        "Prepare personal and household budgets",
                        "Conduct model shopping activities"
                    ],
                    "inquiry_questions": ["How do we calculate profit and loss?", "Why is budgeting important?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Financial literacy", "Consumer awareness"]
                },
            ]
        },
        {
            "name": "Geometry",
            "substrands": [
                {
                    "name": "Lines and Angles",
                    "slos": [
                        {"name": "Identify angle properties", "description": "By the end of the sub-strand the learner should be able to identify angle properties of parallel lines cut by a transversal."},
                        {"name": "Calculate angles", "description": "By the end of the sub-strand the learner should be able to calculate angles formed by parallel lines and transversals."},
                    ],
                    "learning_experiences": [
                        "Identify corresponding angles, alternate angles, and co-interior angles",
                        "Measure angles using protractors",
                        "Calculate unknown angles using angle properties",
                        "Draw parallel lines cut by transversals"
                    ],
                    "inquiry_questions": ["What are the properties of angles formed by parallel lines?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and imagination"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": []
                },
                {
                    "name": "Triangles",
                    "slos": [
                        {"name": "Identify properties of triangles", "description": "By the end of the sub-strand the learner should be able to identify properties of different types of triangles."},
                        {"name": "Calculate angles in triangles", "description": "By the end of the sub-strand the learner should be able to calculate angles in triangles."},
                        {"name": "Construct triangles", "description": "By the end of the sub-strand the learner should be able to construct triangles given specific conditions."},
                    ],
                    "learning_experiences": [
                        "Identify scalene, isosceles, equilateral, acute, right, and obtuse triangles",
                        "Calculate interior and exterior angles of triangles",
                        "Construct triangles using ruler and compass",
                        "Solve problems involving triangle properties"
                    ],
                    "inquiry_questions": ["What are the properties of different types of triangles?", "How do we construct triangles?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and imagination"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": []
                },
                {
                    "name": "Quadrilaterals",
                    "slos": [
                        {"name": "Identify properties of quadrilaterals", "description": "By the end of the sub-strand the learner should be able to identify properties of different quadrilaterals."},
                        {"name": "Calculate angles in quadrilaterals", "description": "By the end of the sub-strand the learner should be able to calculate angles in quadrilaterals."},
                        {"name": "Construct quadrilaterals", "description": "By the end of the sub-strand the learner should be able to construct quadrilaterals given specific conditions."},
                    ],
                    "learning_experiences": [
                        "Identify properties of parallelograms, rectangles, squares, rhombus, trapezium, and kite",
                        "Calculate interior angles of quadrilaterals",
                        "Construct quadrilaterals using ruler and compass",
                        "Solve problems involving quadrilateral properties"
                    ],
                    "inquiry_questions": ["What are the properties of different quadrilaterals?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and imagination"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": []
                },
                {
                    "name": "Circles",
                    "slos": [
                        {"name": "Identify parts of a circle", "description": "By the end of the sub-strand the learner should be able to identify parts of a circle including radius, diameter, chord, arc, sector and segment."},
                        {"name": "Calculate circumference and arc length", "description": "By the end of the sub-strand the learner should be able to calculate circumference and arc length of circles."},
                        {"name": "Calculate area of sectors", "description": "By the end of the sub-strand the learner should be able to calculate area of sectors."},
                    ],
                    "learning_experiences": [
                        "Identify and label parts of a circle",
                        "Calculate circumference using C = 2πr or C = πd",
                        "Calculate arc length",
                        "Calculate area of sectors",
                        "Solve problems involving circles"
                    ],
                    "inquiry_questions": ["What are the parts of a circle?", "How do we calculate circumference and area of sectors?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and imagination"],
                    "values": ["Responsibility"],
                    "pcis": []
                },
                {
                    "name": "Scale Drawing",
                    "slos": [
                        {"name": "Interpret scale drawings", "description": "By the end of the sub-strand the learner should be able to interpret scale drawings."},
                        {"name": "Draw to scale", "description": "By the end of the sub-strand the learner should be able to draw objects to scale."},
                        {"name": "Calculate actual measurements from scale drawings", "description": "By the end of the sub-strand the learner should be able to calculate actual measurements from scale drawings."},
                    ],
                    "learning_experiences": [
                        "Interpret maps and plans using scale",
                        "Draw objects to a given scale",
                        "Calculate actual distances from maps",
                        "Create scale drawings of familiar places"
                    ],
                    "inquiry_questions": ["Why do we use scale drawings?", "How do we interpret scale drawings?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and imagination"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": ["Environmental education"]
                },
                {
                    "name": "Pythagoras Theorem",
                    "slos": [
                        {"name": "State Pythagoras theorem", "description": "By the end of the sub-strand the learner should be able to state Pythagoras theorem."},
                        {"name": "Apply Pythagoras theorem", "description": "By the end of the sub-strand the learner should be able to apply Pythagoras theorem to calculate sides of right-angled triangles."},
                    ],
                    "learning_experiences": [
                        "Discover Pythagoras theorem through practical activities",
                        "State the relationship a² + b² = c²",
                        "Calculate the hypotenuse of right-angled triangles",
                        "Calculate other sides using Pythagoras theorem",
                        "Apply Pythagoras theorem in real life problems"
                    ],
                    "inquiry_questions": ["What is Pythagoras theorem?", "Where do we apply Pythagoras theorem?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Data Handling and Probability",
            "substrands": [
                {
                    "name": "Data Collection and Organization",
                    "slos": [
                        {"name": "Collect data using various methods", "description": "By the end of the sub-strand the learner should be able to collect data using questionnaires, interviews and observation."},
                        {"name": "Organize data in frequency tables", "description": "By the end of the sub-strand the learner should be able to organize data in frequency distribution tables."},
                    ],
                    "learning_experiences": [
                        "Design questionnaires for data collection",
                        "Conduct interviews to collect data",
                        "Collect data through observation",
                        "Organize data in frequency tables",
                        "Create grouped frequency distributions"
                    ],
                    "inquiry_questions": ["How do we collect data?", "How do we organize data?"],
                    "core_competencies": ["Communication and collaboration", "Digital literacy"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": []
                },
                {
                    "name": "Data Representation",
                    "slos": [
                        {"name": "Represent data using bar graphs", "description": "By the end of the sub-strand the learner should be able to represent data using bar graphs."},
                        {"name": "Represent data using pie charts", "description": "By the end of the sub-strand the learner should be able to represent data using pie charts."},
                        {"name": "Represent data using histograms", "description": "By the end of the sub-strand the learner should be able to represent data using histograms."},
                        {"name": "Interpret statistical graphs", "description": "By the end of the sub-strand the learner should be able to interpret information from statistical graphs."},
                    ],
                    "learning_experiences": [
                        "Draw bar graphs to represent data",
                        "Draw pie charts calculating angles",
                        "Draw histograms for grouped data",
                        "Draw frequency polygons",
                        "Interpret data from graphs and charts"
                    ],
                    "inquiry_questions": ["How do we represent data graphically?", "What information can we get from graphs?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and imagination"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": []
                },
                {
                    "name": "Measures of Central Tendency",
                    "slos": [
                        {"name": "Calculate mean of grouped data", "description": "By the end of the sub-strand the learner should be able to calculate the mean of grouped data."},
                        {"name": "Determine median of grouped data", "description": "By the end of the sub-strand the learner should be able to determine the median of grouped data."},
                        {"name": "Determine modal class", "description": "By the end of the sub-strand the learner should be able to determine the modal class of grouped data."},
                    ],
                    "learning_experiences": [
                        "Calculate mean of ungrouped and grouped data",
                        "Determine median of ungrouped and grouped data",
                        "Identify mode and modal class",
                        "Apply measures of central tendency to real data"
                    ],
                    "inquiry_questions": ["How do we calculate measures of central tendency?", "When do we use mean, median and mode?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": []
                },
                {
                    "name": "Probability",
                    "slos": [
                        {"name": "Define probability terms", "description": "By the end of the sub-strand the learner should be able to define experimental and theoretical probability."},
                        {"name": "Calculate probability of simple events", "description": "By the end of the sub-strand the learner should be able to calculate probability of simple events."},
                        {"name": "Apply probability in predictions", "description": "By the end of the sub-strand the learner should be able to apply probability in making predictions."},
                    ],
                    "learning_experiences": [
                        "Conduct experiments to determine experimental probability",
                        "Calculate theoretical probability of events",
                        "Use probability scale from 0 to 1",
                        "Apply probability in decision making",
                        "Play games involving probability"
                    ],
                    "inquiry_questions": ["What is probability?", "How do we calculate probability?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": []
                },
            ]
        },
    ]
}


# ============================================================================
# INTEGRATED SCIENCE GRADE 8 - Parsed from PDF
# ============================================================================
INTEGRATED_SCIENCE_GRADE_8 = {
    "name": "Integrated Science",
    "strands": [
        {
            "name": "Mixtures, Elements and Compounds",
            "substrands": [
                {
                    "name": "Elements and Compounds",
                    "slos": [
                        {"name": "Explain atoms, elements, molecules and compounds", "description": "By the end of the sub strand, the learner should be able to explain the relationship between an atom, an element, a molecule and a compound."},
                        {"name": "Assign symbols to elements", "description": "By the end of the sub strand, the learner should be able to assign symbols to selected elements."},
                        {"name": "Write word equations for reactions", "description": "By the end of the sub strand, the learner should be able to write word equations to represent reactions of selected elements to form compounds."},
                        {"name": "Outline applications of common elements", "description": "By the end of the sub strand, the learner should be able to outline the applications of common elements in the society."},
                    ],
                    "learning_experiences": [
                        "Discuss the meaning of atoms, elements, molecules and compounds",
                        "Collaboratively sample labelled containers of different substances, identify and record the elements or compounds on the containers",
                        "Collaboratively represent selected elements using symbols",
                        "Use word equations to represent reactions of elements to form compounds",
                        "Identify elements in selected compounds (compounds with only two elements)",
                        "Explore the importance and value of common elements and compounds in day-to-day life",
                        "Use digital or print media to search for information on atoms, elements, molecules and compounds"
                    ],
                    "inquiry_questions": ["Why is it important to use symbols for representing elements in day to day life?"],
                    "core_competencies": ["Learning to learn", "Communication and collaboration"],
                    "values": ["Unity - cooperating and harmoniously working with others"],
                    "pcis": ["Financial literacy - exploring value of common elements and compounds"]
                },
                {
                    "name": "Physical and Chemical Changes",
                    "slos": [
                        {"name": "Describe characteristics of particles in states of matter", "description": "By the end of the sub strand, the learner should be able to describe the characteristics of particles in the three states of matter."},
                        {"name": "Explain effects of impurities on boiling and melting points", "description": "By the end of the sub strand, the learner should be able to explain the effects of impurities on boiling point and melting point of a substance."},
                        {"name": "Distinguish physical and chemical changes", "description": "By the end of the sub strand, the learner should be able to distinguish between physical and chemical changes in substances."},
                        {"name": "Outline applications of change of state", "description": "By the end of the sub strand, the learner should be able to outline applications of change of state of matter in day-to-day life."},
                    ],
                    "learning_experiences": [
                        "Carry out activities to demonstrate the characteristics of particles in the three states of matter",
                        "Perform experiments to demonstrate diffusion in liquids and gases using water and ink",
                        "Carry out experiments to determine the boiling and melting points of pure and impure substances",
                        "Draw the heating curve and discuss the trends",
                        "Discuss the effects of impurities on boiling point and melting point of a substance",
                        "Carry out experiments to distinguish physical and chemical changes",
                        "Observe and record changes that occur during physical and chemical changes"
                    ],
                    "inquiry_questions": ["How does the movement of particles in matter affect its properties?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Environmental education"]
                },
                {
                    "name": "Classes of Fire",
                    "slos": [
                        {"name": "Identify classes of fire", "description": "By the end of the sub strand, the learner should be able to identify the different classes of fire."},
                        {"name": "Identify causes of fire", "description": "By the end of the sub strand, the learner should be able to identify causes of fire in different situations."},
                        {"name": "Select appropriate fire extinguishing methods", "description": "By the end of the sub strand, the learner should be able to select appropriate methods of extinguishing different classes of fire."},
                        {"name": "Demonstrate fire safety measures", "description": "By the end of the sub strand, the learner should be able to demonstrate fire safety measures."},
                    ],
                    "learning_experiences": [
                        "Discuss and classify fires according to their causes (Class A, B, C, D, K)",
                        "Investigate causes of fire in the home, school and community",
                        "Identify fire extinguishing methods suitable for different classes of fire",
                        "Demonstrate use of fire extinguishers",
                        "Practice fire drills and evacuation procedures",
                        "Create fire safety awareness campaigns"
                    ],
                    "inquiry_questions": ["How do we prevent and control fires?", "What are the different classes of fire?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility", "Safety consciousness"],
                    "pcis": ["Safety and security education", "Disaster risk reduction"]
                },
            ]
        },
        {
            "name": "Living Things and the Environment",
            "substrands": [
                {
                    "name": "The Cell",
                    "slos": [
                        {"name": "Describe cell structure", "description": "By the end of the sub strand, the learner should be able to describe the structure of plant and animal cells."},
                        {"name": "Identify functions of cell parts", "description": "By the end of the sub strand, the learner should be able to identify the functions of different cell parts."},
                        {"name": "Compare plant and animal cells", "description": "By the end of the sub strand, the learner should be able to compare plant and animal cells."},
                        {"name": "Observe cells under microscope", "description": "By the end of the sub strand, the learner should be able to observe cells under a microscope."},
                    ],
                    "learning_experiences": [
                        "Prepare slides of plant and animal cells for observation",
                        "Observe plant and animal cells under a microscope",
                        "Draw and label parts of plant and animal cells",
                        "Discuss functions of cell membrane, cell wall, nucleus, cytoplasm, vacuole, chloroplast, mitochondria",
                        "Compare and contrast plant and animal cells using diagrams",
                        "Use digital resources to explore cell structure"
                    ],
                    "inquiry_questions": ["What are the parts of a cell?", "How do plant and animal cells differ?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Curiosity"],
                    "pcis": ["Health education"]
                },
                {
                    "name": "Movement of Materials In and Out of the Cell",
                    "slos": [
                        {"name": "Explain diffusion", "description": "By the end of the sub strand, the learner should be able to explain diffusion and its importance in living things."},
                        {"name": "Explain osmosis", "description": "By the end of the sub strand, the learner should be able to explain osmosis and its effects on cells."},
                        {"name": "Demonstrate diffusion and osmosis", "description": "By the end of the sub strand, the learner should be able to demonstrate diffusion and osmosis through experiments."},
                    ],
                    "learning_experiences": [
                        "Carry out experiments to demonstrate diffusion in liquids and gases",
                        "Carry out experiments to demonstrate osmosis using visking tubing or potato strips",
                        "Observe effects of osmosis on plant and animal cells",
                        "Discuss the importance of diffusion and osmosis in living organisms",
                        "Relate diffusion and osmosis to everyday life examples"
                    ],
                    "inquiry_questions": ["How do substances move in and out of cells?", "What is the difference between diffusion and osmosis?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Curiosity"],
                    "pcis": ["Health education"]
                },
                {
                    "name": "Reproduction in Human Beings",
                    "slos": [
                        {"name": "Describe male and female reproductive systems", "description": "By the end of the sub strand, the learner should be able to describe the structure and function of male and female reproductive systems."},
                        {"name": "Explain fertilization and pregnancy", "description": "By the end of the sub strand, the learner should be able to explain the process of fertilization and pregnancy."},
                        {"name": "Discuss adolescent changes", "description": "By the end of the sub strand, the learner should be able to discuss physical and emotional changes during adolescence."},
                        {"name": "Identify reproductive health issues", "description": "By the end of the sub strand, the learner should be able to identify reproductive health issues affecting adolescents."},
                    ],
                    "learning_experiences": [
                        "Draw and label parts of male and female reproductive systems",
                        "Discuss functions of parts of the reproductive systems",
                        "Explain the menstrual cycle",
                        "Discuss the process of fertilization and implantation",
                        "Discuss stages of pregnancy and fetal development",
                        "Discuss physical and emotional changes during puberty",
                        "Discuss adolescent reproductive health issues including STIs and teenage pregnancy"
                    ],
                    "inquiry_questions": ["How does human reproduction occur?", "What changes occur during adolescence?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Respect", "Responsibility"],
                    "pcis": ["Health education", "HIV/AIDS education", "Life skills"]
                },
            ]
        },
        {
            "name": "Force and Energy",
            "substrands": [
                {
                    "name": "Transformation of Energy",
                    "slos": [
                        {"name": "Identify forms of energy", "description": "By the end of the sub strand, the learner should be able to identify different forms of energy."},
                        {"name": "Describe energy transformations", "description": "By the end of the sub strand, the learner should be able to describe energy transformations in different devices."},
                        {"name": "Explain law of conservation of energy", "description": "By the end of the sub strand, the learner should be able to explain the law of conservation of energy."},
                        {"name": "Discuss renewable and non-renewable energy", "description": "By the end of the sub strand, the learner should be able to discuss renewable and non-renewable sources of energy."},
                    ],
                    "learning_experiences": [
                        "Identify different forms of energy: kinetic, potential, heat, light, sound, electrical, chemical, nuclear",
                        "Demonstrate energy transformations using devices like torches, radios, electric heaters",
                        "Trace energy transformations in power stations",
                        "Discuss the law of conservation of energy",
                        "Classify energy sources as renewable or non-renewable",
                        "Research on renewable energy sources in Kenya"
                    ],
                    "inquiry_questions": ["What are the different forms of energy?", "How is energy transformed from one form to another?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Environmental awareness"],
                    "pcis": ["Environmental education", "Energy conservation"]
                },
                {
                    "name": "Pressure",
                    "slos": [
                        {"name": "Define pressure", "description": "By the end of the sub strand, the learner should be able to define pressure and state its SI unit."},
                        {"name": "Calculate pressure", "description": "By the end of the sub strand, the learner should be able to calculate pressure in different situations."},
                        {"name": "Explain applications of pressure", "description": "By the end of the sub strand, the learner should be able to explain applications of pressure in solids, liquids and gases."},
                    ],
                    "learning_experiences": [
                        "Define pressure as force per unit area",
                        "Calculate pressure using P = F/A",
                        "Demonstrate pressure in solids using blocks on soft surfaces",
                        "Investigate liquid pressure at different depths",
                        "Demonstrate gas pressure using syringes and balloons",
                        "Discuss applications of pressure: hydraulic systems, pneumatic systems, atmospheric pressure"
                    ],
                    "inquiry_questions": ["What is pressure?", "How is pressure applied in everyday life?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Curiosity"],
                    "pcis": []
                },
            ]
        },
    ]
}


# ============================================================================
# SOCIAL STUDIES GRADE 8 - Parsed from PDF
# ============================================================================
SOCIAL_STUDIES_GRADE_8 = {
    "name": "Social Studies",
    "strands": [
        {
            "name": "Environment and Resources",
            "substrands": [
                {
                    "name": "Climate and Weather",
                    "slos": [
                        {"name": "Distinguish weather from climate", "description": "By the end of the sub strand, the learner should be able to distinguish between weather and climate."},
                        {"name": "Identify elements of weather", "description": "By the end of the sub strand, the learner should be able to identify elements of weather."},
                        {"name": "Describe instruments for measuring weather", "description": "By the end of the sub strand, the learner should be able to describe instruments used for measuring weather elements."},
                        {"name": "Explain factors influencing climate", "description": "By the end of the sub strand, the learner should be able to explain factors influencing climate of an area."},
                    ],
                    "learning_experiences": [
                        "Discuss the difference between weather and climate",
                        "Identify and describe elements of weather: temperature, rainfall, humidity, wind, air pressure",
                        "Describe instruments used to measure weather elements",
                        "Set up a simple weather station in school",
                        "Record and analyze weather data",
                        "Discuss factors influencing climate: latitude, altitude, distance from sea, ocean currents, prevailing winds"
                    ],
                    "inquiry_questions": ["What is the difference between weather and climate?", "What instruments are used to measure weather?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Environmental awareness"],
                    "pcis": ["Environmental education", "Climate change education"]
                },
                {
                    "name": "Vegetation in Africa",
                    "slos": [
                        {"name": "Identify vegetation zones in Africa", "description": "By the end of the sub strand, the learner should be able to identify vegetation zones in Africa."},
                        {"name": "Describe characteristics of vegetation zones", "description": "By the end of the sub strand, the learner should be able to describe characteristics of different vegetation zones."},
                        {"name": "Explain importance of vegetation", "description": "By the end of the sub strand, the learner should be able to explain the importance of vegetation."},
                    ],
                    "learning_experiences": [
                        "Identify vegetation zones on a map of Africa: tropical forests, savanna, desert, Mediterranean, montane",
                        "Describe characteristics of each vegetation zone",
                        "Discuss factors influencing distribution of vegetation",
                        "Explain importance of vegetation to humans and the environment",
                        "Discuss threats to vegetation and conservation measures"
                    ],
                    "inquiry_questions": ["What are the vegetation zones in Africa?", "Why is vegetation important?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Environmental awareness", "Responsibility"],
                    "pcis": ["Environmental education", "Conservation"]
                },
                {
                    "name": "Mineral Resources",
                    "slos": [
                        {"name": "Identify mineral resources in Africa", "description": "By the end of the sub strand, the learner should be able to identify major mineral resources in Africa."},
                        {"name": "Describe methods of mining", "description": "By the end of the sub strand, the learner should be able to describe different methods of mining."},
                        {"name": "Explain contribution of mining to economy", "description": "By the end of the sub strand, the learner should be able to explain the contribution of mining to the economy."},
                        {"name": "Discuss effects of mining", "description": "By the end of the sub strand, the learner should be able to discuss positive and negative effects of mining."},
                    ],
                    "learning_experiences": [
                        "Identify major mineral resources in Africa and their locations",
                        "Describe methods of mining: open cast, underground, dredging, drilling",
                        "Discuss the contribution of mining to African economies",
                        "Analyze positive and negative effects of mining",
                        "Discuss sustainable mining practices"
                    ],
                    "inquiry_questions": ["What mineral resources are found in Africa?", "How does mining contribute to economic development?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Environmental awareness"],
                    "pcis": ["Environmental education", "Financial literacy"]
                },
            ]
        },
        {
            "name": "Population and Development",
            "substrands": [
                {
                    "name": "Population Distribution and Characteristics",
                    "slos": [
                        {"name": "Describe population distribution in Africa", "description": "By the end of the sub strand, the learner should be able to describe population distribution in Africa."},
                        {"name": "Explain factors affecting population distribution", "description": "By the end of the sub strand, the learner should be able to explain factors affecting population distribution."},
                        {"name": "Analyze population characteristics", "description": "By the end of the sub strand, the learner should be able to analyze population characteristics including age structure and sex ratio."},
                    ],
                    "learning_experiences": [
                        "Study population distribution maps of Africa",
                        "Identify densely and sparsely populated areas",
                        "Discuss factors affecting population distribution: climate, relief, soils, resources, historical factors",
                        "Analyze population pyramids",
                        "Calculate and interpret population density"
                    ],
                    "inquiry_questions": ["What factors influence population distribution?", "How do we describe population characteristics?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility"],
                    "pcis": ["Population education"]
                },
                {
                    "name": "Urbanization",
                    "slos": [
                        {"name": "Define urbanization", "description": "By the end of the sub strand, the learner should be able to define urbanization."},
                        {"name": "Explain causes of urbanization", "description": "By the end of the sub strand, the learner should be able to explain causes of urbanization in Africa."},
                        {"name": "Discuss effects of urbanization", "description": "By the end of the sub strand, the learner should be able to discuss positive and negative effects of urbanization."},
                        {"name": "Suggest solutions to urban challenges", "description": "By the end of the sub strand, the learner should be able to suggest solutions to challenges of urbanization."},
                    ],
                    "learning_experiences": [
                        "Define urbanization and identify major urban centers in Africa",
                        "Discuss causes of rural-urban migration",
                        "Analyze effects of urbanization: growth of slums, pollution, unemployment, crime, improved services",
                        "Suggest solutions to urban challenges",
                        "Case study of urbanization in a selected African city"
                    ],
                    "inquiry_questions": ["What causes urbanization?", "How can urban challenges be addressed?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility", "Citizenship"],
                    "pcis": ["Population education", "Environmental education"]
                },
            ]
        },
        {
            "name": "Historical Development",
            "substrands": [
                {
                    "name": "Early Human Beings and Society",
                    "slos": [
                        {"name": "Describe evolution of human beings", "description": "By the end of the sub strand, the learner should be able to describe the evolution of human beings."},
                        {"name": "Identify archaeological sites in Africa", "description": "By the end of the sub strand, the learner should be able to identify major archaeological sites in Africa."},
                        {"name": "Explain development of early societies", "description": "By the end of the sub strand, the learner should be able to explain the development of early human societies."},
                    ],
                    "learning_experiences": [
                        "Discuss theories of evolution of human beings",
                        "Identify major archaeological sites in Africa: Olduvai Gorge, Koobi Fora, Olorgesailie",
                        "Describe characteristics of early human ancestors",
                        "Discuss development of early human societies and civilizations",
                        "Visit archaeological sites or museums (where possible)"
                    ],
                    "inquiry_questions": ["How did human beings evolve?", "What do archaeological sites tell us about early humans?"],
                    "core_competencies": ["Learning to learn", "Digital literacy"],
                    "values": ["Respect for heritage", "Curiosity"],
                    "pcis": ["Heritage conservation"]
                },
                {
                    "name": "External Contacts and Colonization",
                    "slos": [
                        {"name": "Describe external contacts with Africa", "description": "By the end of the sub strand, the learner should be able to describe early external contacts with Africa."},
                        {"name": "Explain causes of colonization", "description": "By the end of the sub strand, the learner should be able to explain causes of colonization of Africa."},
                        {"name": "Analyze effects of colonization", "description": "By the end of the sub strand, the learner should be able to analyze effects of colonization on African societies."},
                    ],
                    "learning_experiences": [
                        "Discuss early external contacts: Arabs, Europeans, Asians",
                        "Trace the slave trade and its effects",
                        "Explain the scramble for and partition of Africa",
                        "Analyze political, economic, and social effects of colonization",
                        "Discuss African resistance to colonization"
                    ],
                    "inquiry_questions": ["How did external contacts affect Africa?", "What were the effects of colonization?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Patriotism", "Social justice"],
                    "pcis": ["Peace education", "Human rights"]
                },
            ]
        },
        {
            "name": "Governance and Citizenship",
            "substrands": [
                {
                    "name": "Democracy and Human Rights",
                    "slos": [
                        {"name": "Define democracy", "description": "By the end of the sub strand, the learner should be able to define democracy and its principles."},
                        {"name": "Explain types of democracy", "description": "By the end of the sub strand, the learner should be able to explain different types of democracy."},
                        {"name": "Identify human rights", "description": "By the end of the sub strand, the learner should be able to identify fundamental human rights."},
                        {"name": "Discuss role of citizens in democracy", "description": "By the end of the sub strand, the learner should be able to discuss the role of citizens in a democracy."},
                    ],
                    "learning_experiences": [
                        "Define democracy and discuss its key principles",
                        "Compare direct and representative democracy",
                        "Identify fundamental human rights as outlined in constitutions",
                        "Discuss responsibilities of citizens in a democracy",
                        "Practice democratic processes through class elections"
                    ],
                    "inquiry_questions": ["What is democracy?", "What are the rights and responsibilities of citizens?"],
                    "core_competencies": ["Citizenship", "Communication and collaboration"],
                    "values": ["Patriotism", "Respect", "Social justice"],
                    "pcis": ["Civic education", "Human rights"]
                },
                {
                    "name": "Regional and International Organizations",
                    "slos": [
                        {"name": "Identify regional organizations in Africa", "description": "By the end of the sub strand, the learner should be able to identify regional organizations in Africa."},
                        {"name": "Explain role of regional organizations", "description": "By the end of the sub strand, the learner should be able to explain the role of regional organizations in promoting development."},
                        {"name": "Discuss challenges facing regional organizations", "description": "By the end of the sub strand, the learner should be able to discuss challenges facing regional organizations."},
                    ],
                    "learning_experiences": [
                        "Identify regional organizations: AU, EAC, ECOWAS, SADC",
                        "Discuss objectives and functions of regional organizations",
                        "Analyze benefits of regional cooperation",
                        "Discuss challenges facing regional organizations",
                        "Explore Kenya's role in regional organizations"
                    ],
                    "inquiry_questions": ["Why are regional organizations important?", "What challenges do they face?"],
                    "core_competencies": ["Critical thinking and problem solving", "Citizenship"],
                    "values": ["Patriotism", "Unity", "Cooperation"],
                    "pcis": ["Peace education", "Regional integration"]
                },
            ]
        },
    ]
}


# ============================================================================
# ENGLISH GRADE 8 - Parsed from PDF
# ============================================================================
ENGLISH_GRADE_8 = {
    "name": "English",
    "strands": [
        {
            "name": "Listening and Speaking",
            "substrands": [
                {
                    "name": "Listening Comprehension",
                    "slos": [
                        {"name": "Listen for specific information", "description": "By the end of the sub strand, the learner should be able to listen for specific information from various sources."},
                        {"name": "Identify main ideas and details", "description": "By the end of the sub strand, the learner should be able to identify main ideas and supporting details from listening texts."},
                        {"name": "Make inferences from listening", "description": "By the end of the sub strand, the learner should be able to make inferences from spoken texts."},
                    ],
                    "learning_experiences": [
                        "Listen to audio recordings and identify specific information",
                        "Listen to stories and summarize main ideas",
                        "Practice note-taking while listening",
                        "Participate in listening comprehension exercises",
                        "Respond to questions based on listening texts"
                    ],
                    "inquiry_questions": ["How do we listen effectively?", "Why is listening important in communication?"],
                    "core_competencies": ["Communication and collaboration", "Learning to learn"],
                    "values": ["Respect", "Attentiveness"],
                    "pcis": []
                },
                {
                    "name": "Oral Communication",
                    "slos": [
                        {"name": "Speak fluently and clearly", "description": "By the end of the sub strand, the learner should be able to speak fluently and clearly in various contexts."},
                        {"name": "Use appropriate language in discussions", "description": "By the end of the sub strand, the learner should be able to use appropriate language in group discussions."},
                        {"name": "Present information effectively", "description": "By the end of the sub strand, the learner should be able to present information effectively to different audiences."},
                    ],
                    "learning_experiences": [
                        "Participate in class discussions and debates",
                        "Give oral presentations on various topics",
                        "Practice pronunciation and articulation",
                        "Role play different communication scenarios",
                        "Conduct interviews and report findings"
                    ],
                    "inquiry_questions": ["How can we improve our speaking skills?", "What makes an effective presentation?"],
                    "core_competencies": ["Communication and collaboration", "Self-efficacy"],
                    "values": ["Confidence", "Respect"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Reading",
            "substrands": [
                {
                    "name": "Reading Comprehension",
                    "slos": [
                        {"name": "Read fluently with expression", "description": "By the end of the sub strand, the learner should be able to read fluently with appropriate expression."},
                        {"name": "Identify main ideas and supporting details", "description": "By the end of the sub strand, the learner should be able to identify main ideas and supporting details in texts."},
                        {"name": "Make inferences and predictions", "description": "By the end of the sub strand, the learner should be able to make inferences and predictions from texts."},
                        {"name": "Analyze text features", "description": "By the end of the sub strand, the learner should be able to analyze various text features."},
                    ],
                    "learning_experiences": [
                        "Read passages aloud with appropriate expression",
                        "Answer comprehension questions based on reading",
                        "Practice different reading strategies: skimming, scanning, intensive reading",
                        "Analyze text features: headings, subheadings, diagrams, graphs",
                        "Summarize and paraphrase reading texts"
                    ],
                    "inquiry_questions": ["How do we understand what we read?", "What strategies help us read better?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving"],
                    "values": ["Appreciation of literature", "Curiosity"],
                    "pcis": []
                },
                {
                    "name": "Extensive Reading",
                    "slos": [
                        {"name": "Read for enjoyment", "description": "By the end of the sub strand, the learner should be able to read extensively for enjoyment."},
                        {"name": "Analyze characters and themes", "description": "By the end of the sub strand, the learner should be able to analyze characters, themes and settings in literary works."},
                        {"name": "Write book reviews", "description": "By the end of the sub strand, the learner should be able to write book reviews and recommendations."},
                    ],
                    "learning_experiences": [
                        "Read set books and other literary works",
                        "Discuss plot, characters, themes, and settings",
                        "Write book reviews and summaries",
                        "Participate in book clubs and reading circles",
                        "Maintain a reading journal"
                    ],
                    "inquiry_questions": ["Why is reading for enjoyment important?", "How do we analyze literary works?"],
                    "core_competencies": ["Learning to learn", "Creativity and imagination"],
                    "values": ["Appreciation of literature", "Critical thinking"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Grammar",
            "substrands": [
                {
                    "name": "Sentence Structure",
                    "slos": [
                        {"name": "Construct different types of sentences", "description": "By the end of the sub strand, the learner should be able to construct simple, compound and complex sentences."},
                        {"name": "Identify sentence elements", "description": "By the end of the sub strand, the learner should be able to identify subject, verb, object, complement and adverbials in sentences."},
                    ],
                    "learning_experiences": [
                        "Identify parts of a sentence",
                        "Construct simple, compound and complex sentences",
                        "Combine sentences using conjunctions",
                        "Practice sentence transformation exercises",
                        "Analyze sentence structure in reading texts"
                    ],
                    "inquiry_questions": ["What are the different types of sentences?", "How do we construct complex sentences?"],
                    "core_competencies": ["Communication and collaboration", "Learning to learn"],
                    "values": ["Accuracy", "Clarity"],
                    "pcis": []
                },
                {
                    "name": "Tenses",
                    "slos": [
                        {"name": "Use present tenses correctly", "description": "By the end of the sub strand, the learner should be able to use present tenses correctly in communication."},
                        {"name": "Use past tenses correctly", "description": "By the end of the sub strand, the learner should be able to use past tenses correctly in communication."},
                        {"name": "Use future tenses correctly", "description": "By the end of the sub strand, the learner should be able to use future tenses correctly in communication."},
                    ],
                    "learning_experiences": [
                        "Practice using present simple, present continuous, present perfect",
                        "Practice using past simple, past continuous, past perfect",
                        "Practice using future simple, future continuous",
                        "Complete tense exercises and gap-fills",
                        "Apply correct tenses in writing and speaking"
                    ],
                    "inquiry_questions": ["When do we use different tenses?", "How do tenses change meaning?"],
                    "core_competencies": ["Communication and collaboration", "Learning to learn"],
                    "values": ["Accuracy"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Writing",
            "substrands": [
                {
                    "name": "Creative Writing",
                    "slos": [
                        {"name": "Write narratives", "description": "By the end of the sub strand, the learner should be able to write engaging narratives with clear structure."},
                        {"name": "Write descriptions", "description": "By the end of the sub strand, the learner should be able to write vivid descriptions using appropriate language."},
                        {"name": "Write poetry", "description": "By the end of the sub strand, the learner should be able to write poems using various poetic devices."},
                    ],
                    "learning_experiences": [
                        "Write short stories with clear beginning, middle and end",
                        "Write descriptive essays using sensory details",
                        "Write poems using rhyme, rhythm and imagery",
                        "Peer review and edit creative writing",
                        "Participate in creative writing competitions"
                    ],
                    "inquiry_questions": ["What makes writing creative?", "How do we improve our writing?"],
                    "core_competencies": ["Creativity and imagination", "Communication and collaboration"],
                    "values": ["Creativity", "Self-expression"],
                    "pcis": []
                },
                {
                    "name": "Functional Writing",
                    "slos": [
                        {"name": "Write formal letters", "description": "By the end of the sub strand, the learner should be able to write formal letters for various purposes."},
                        {"name": "Write reports", "description": "By the end of the sub strand, the learner should be able to write reports with appropriate format and content."},
                        {"name": "Fill in forms", "description": "By the end of the sub strand, the learner should be able to fill in various forms accurately."},
                    ],
                    "learning_experiences": [
                        "Write formal letters: application letters, complaint letters, inquiry letters",
                        "Write reports: incident reports, field trip reports",
                        "Fill in application forms, registration forms",
                        "Write emails for formal communication",
                        "Practice formatting different types of functional writing"
                    ],
                    "inquiry_questions": ["What are the features of formal writing?", "Why is functional writing important?"],
                    "core_competencies": ["Communication and collaboration", "Digital literacy"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": ["Consumer awareness", "Career guidance"]
                },
            ]
        },
    ]
}


# ============================================================================
# KISWAHILI GRADE 8 - Parsed from PDF
# ============================================================================
KISWAHILI_GRADE_8 = {
    "name": "Kiswahili",
    "strands": [
        {
            "name": "Kusikiliza na Kuongea (Listening and Speaking)",
            "substrands": [
                {
                    "name": "Kusikiliza kwa Ufahamu",
                    "slos": [
                        {"name": "Sikiliza kwa ufahamu habari mbalimbali", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kusikiliza kwa ufahamu habari mbalimbali."},
                        {"name": "Bainisha wazo kuu na mawazo mengine", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kubainisha wazo kuu na mawazo mengine kutoka kwenye habari."},
                    ],
                    "learning_experiences": [
                        "Kusikiliza habari kutoka vyanzo mbalimbali",
                        "Kujibu maswali kuhusu habari iliyosikilizwa",
                        "Kubainisha wazo kuu na mawazo mengine",
                        "Kujadili maudhui ya habari zilizosikilizwa"
                    ],
                    "inquiry_questions": ["Tunawezaje kusikiliza kwa ufahamu?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujifunza kujifunza"],
                    "values": ["Heshima", "Umakinifu"],
                    "pcis": []
                },
                {
                    "name": "Mazungumzo",
                    "slos": [
                        {"name": "Ongea kwa ufasaha kuhusu mada mbalimbali", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuongea kwa ufasaha kuhusu mada mbalimbali."},
                        {"name": "Tumia lugha ya heshima katika mazungumzo", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutumia lugha ya heshima katika mazungumzo."},
                    ],
                    "learning_experiences": [
                        "Kushiriki katika majadiliano ya darasani",
                        "Kutoa hotuba kuhusu mada mbalimbali",
                        "Kuigiza hali mbalimbali za mawasiliano",
                        "Kufanya mahojiano na kuripoti matokeo"
                    ],
                    "inquiry_questions": ["Tunawezaje kuboresha uwezo wetu wa kuongea?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujiamini"],
                    "values": ["Ujasiri", "Heshima"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Kusoma (Reading)",
            "substrands": [
                {
                    "name": "Kusoma kwa Ufahamu",
                    "slos": [
                        {"name": "Soma kwa ufasaha na sauti inayofaa", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kusoma kwa ufasaha na sauti inayofaa."},
                        {"name": "Bainisha wazo kuu na mawazo mengine", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kubainisha wazo kuu na mawazo mengine katika matini."},
                        {"name": "Eleza maana za maneno kutoka muktadha", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kueleza maana za maneno kutoka muktadha."},
                    ],
                    "learning_experiences": [
                        "Kusoma vifungu kwa sauti na kimya",
                        "Kujibu maswali ya ufahamu",
                        "Kutumia mikakati mbalimbali ya kusoma",
                        "Kufupisha na kuandika kwa maneno yako"
                    ],
                    "inquiry_questions": ["Tunawezaje kusoma kwa ufahamu?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Fikra makini"],
                    "values": ["Upendaji wa fasihi", "Udadisi"],
                    "pcis": []
                },
                {
                    "name": "Kusoma Kwa Mapana",
                    "slos": [
                        {"name": "Soma vitabu teule kwa furaha", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kusoma vitabu teule kwa furaha."},
                        {"name": "Changanua wahusika na maudhui", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuchanganua wahusika, maudhui na mandhari katika kazi za fasihi."},
                    ],
                    "learning_experiences": [
                        "Kusoma vitabu teule na kazi nyingine za fasihi",
                        "Kujadili ploti, wahusika, maudhui na mandhari",
                        "Kuandika mapitio ya vitabu",
                        "Kushiriki katika vilabu vya kusoma"
                    ],
                    "inquiry_questions": ["Kwa nini kusoma kwa furaha ni muhimu?"],
                    "core_competencies": ["Kujifunza kujifunza", "Ubunifu na mawazo"],
                    "values": ["Upendaji wa fasihi"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Sarufi (Grammar)",
            "substrands": [
                {
                    "name": "Muundo wa Sentensi",
                    "slos": [
                        {"name": "Tunga sentensi sahili, changamano na ambatano", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutunga sentensi sahili, changamano na ambatano."},
                        {"name": "Bainisha sehemu za sentensi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kubainisha sehemu za sentensi: kiima, kiarifu."},
                    ],
                    "learning_experiences": [
                        "Kubainisha sehemu za sentensi",
                        "Kutunga sentensi sahili, changamano na ambatano",
                        "Kuunganisha sentensi kwa kutumia viunganishi",
                        "Kuchanganua muundo wa sentensi katika matini"
                    ],
                    "inquiry_questions": ["Aina za sentensi ni zipi?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujifunza kujifunza"],
                    "values": ["Usahihi", "Uwazi"],
                    "pcis": []
                },
                {
                    "name": "Ngeli za Kiswahili",
                    "slos": [
                        {"name": "Bainisha ngeli mbalimbali za Kiswahili", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kubainisha ngeli mbalimbali za Kiswahili."},
                        {"name": "Tumia ngeli kwa usahihi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutumia ngeli kwa usahihi katika mawasiliano."},
                    ],
                    "learning_experiences": [
                        "Kubainisha ngeli za Kiswahili: A-WA, M-MI, KI-VI, N-N, U-U, PA-KU-M",
                        "Kuweka nomino katika ngeli zake",
                        "Kutumia viambishi vya ngeli kwa usahihi",
                        "Kutunga sentensi zinazofuata sheria za upatanisho wa kisarufi"
                    ],
                    "inquiry_questions": ["Ngeli za Kiswahili ni zipi?", "Kwa nini ngeli ni muhimu?"],
                    "core_competencies": ["Mawasiliano na ushirikiano"],
                    "values": ["Usahihi"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Kuandika (Writing)",
            "substrands": [
                {
                    "name": "Uandishi wa Ubunifu",
                    "slos": [
                        {"name": "Andika insha za masimulizi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuandika insha za masimulizi zenye muundo unaofaa."},
                        {"name": "Andika insha za maelezo", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuandika insha za maelezo kwa lugha fasaha."},
                    ],
                    "learning_experiences": [
                        "Kuandika insha za masimulizi zenye utangulizi, kiini na hitimisho",
                        "Kuandika insha za maelezo kwa kutumia lugha ya picha",
                        "Kuhariri na kusahihisha uandishi wa ubunifu",
                        "Kushiriki katika mashindano ya uandishi"
                    ],
                    "inquiry_questions": ["Uandishi wa ubunifu ni nini?"],
                    "core_competencies": ["Ubunifu na mawazo", "Mawasiliano na ushirikiano"],
                    "values": ["Ubunifu", "Kujieleza"],
                    "pcis": []
                },
                {
                    "name": "Uandishi wa Kiutendaji",
                    "slos": [
                        {"name": "Andika barua rasmi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuandika barua rasmi kwa madhumuni mbalimbali."},
                        {"name": "Andika taarifa", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuandika taarifa zenye muundo na maudhui yanayofaa."},
                    ],
                    "learning_experiences": [
                        "Kuandika barua rasmi: za kuomba kazi, malalamiko, kuuliza",
                        "Kuandika taarifa: za matukio, za ziara",
                        "Kujaza fomu mbalimbali",
                        "Kuandika barua pepe kwa mawasiliano rasmi"
                    ],
                    "inquiry_questions": ["Uandishi rasmi una sifa gani?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Ujuzi wa kidijitali"],
                    "values": ["Uwajibikaji", "Usahihi"],
                    "pcis": ["Ufahamu wa mlaji", "Mwongozo wa kazi"]
                },
            ]
        },
    ]
}


async def clear_subject_curriculum(subject_name, grade_id):
    """Clear existing curriculum data for a subject in a specific grade"""
    subject = await db.subjects.find_one({"name": subject_name})
    if not subject:
        return
    
    subject_id = subject.get('id', str(subject['_id']))
    
    # Get strands for this subject
    strands = await db.strands.find({"subjectId": subject_id}).to_list(None)
    
    deleted_strands = 0
    deleted_substrands = 0
    deleted_slos = 0
    deleted_activities = 0
    
    for strand in strands:
        strand_id = strand.get('id', str(strand['_id']))
        
        # Get substrands
        substrands = await db.substrands.find({"strandId": strand_id}).to_list(None)
        
        for substrand in substrands:
            substrand_id = substrand.get('id', str(substrand['_id']))
            
            # Delete SLOs
            result = await db.slos.delete_many({"substrandId": substrand_id})
            deleted_slos += result.deleted_count
            
            # Delete learning activities
            result = await db.learning_activities.delete_many({"substrandId": substrand_id})
            deleted_activities += result.deleted_count
        
        # Delete substrands
        result = await db.substrands.delete_many({"strandId": strand_id})
        deleted_substrands += result.deleted_count
    
    # Delete strands
    result = await db.strands.delete_many({"subjectId": subject_id})
    deleted_strands += result.deleted_count
    
    print(f"  Cleared: {deleted_strands} strands, {deleted_substrands} substrands, {deleted_slos} SLOs, {deleted_activities} activities")


async def seed_subject_complete(subject_data, grade_id):
    """Seed complete subject data including learning experiences"""
    subject_name = subject_data["name"]
    print(f"\n--- Seeding {subject_name} for Grade 8 ---")
    
    # Clear existing data
    await clear_subject_curriculum(subject_name, grade_id)
    
    # Get or create subject
    subject = await db.subjects.find_one({"name": subject_name})
    if subject:
        subject_id = subject.get('id', str(subject['_id']))
        # Ensure grade_id is in gradeIds
        await db.subjects.update_one(
            {"name": subject_name},
            {"$addToSet": {"gradeIds": grade_id}}
        )
    else:
        subject_id = str(ObjectId())
        await db.subjects.insert_one({
            "id": subject_id,
            "name": subject_name,
            "gradeIds": [grade_id]
        })
        print(f"  Created new subject: {subject_name}")
    
    strands_count = 0
    substrands_count = 0
    slos_count = 0
    activities_count = 0
    
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
            
            # Insert SLOs
            for slo_data in substrand_data["slos"]:
                await db.slos.insert_one({
                    "id": str(ObjectId()),
                    "name": slo_data["name"],
                    "description": slo_data["description"],
                    "substrandId": substrand_id
                })
                slos_count += 1
            
            # Insert Learning Activities
            learning_experiences = substrand_data.get("learning_experiences", [])
            if learning_experiences:
                # Format as structured activities
                introduction = []
                development = []
                conclusion = []
                
                # Distribute learning experiences across phases
                total = len(learning_experiences)
                if total > 0:
                    introduction = learning_experiences[:max(1, total//3)]
                    development = learning_experiences[max(1, total//3):max(2, 2*total//3)]
                    conclusion = learning_experiences[max(2, 2*total//3):]
                
                await db.learning_activities.insert_one({
                    "id": str(ObjectId()),
                    "substrandId": substrand_id,
                    "introduction": introduction,
                    "development": development,
                    "conclusion": conclusion,
                    "extendedActivities": [],
                    "inquiry_questions": substrand_data.get("inquiry_questions", []),
                    "core_competencies": substrand_data.get("core_competencies", []),
                    "values": substrand_data.get("values", []),
                    "pcis": substrand_data.get("pcis", [])
                })
                activities_count += 1
    
    print(f"  Added: {strands_count} strands, {substrands_count} substrands, {slos_count} SLOs, {activities_count} activity sets")
    return strands_count, substrands_count, slos_count, activities_count


async def main():
    """Main function to seed Grade 8 curriculum from uploaded PDFs"""
    print("=" * 70)
    print("SEEDING GRADE 8 CURRICULUM FROM UPLOADED KICD PDFs")
    print("=" * 70)
    
    # Get Grade 8 ID
    grade_8 = await db.grades.find_one({"name": "Grade 8"})
    if not grade_8:
        print("ERROR: Grade 8 not found in database!")
        return
    
    grade_8_id = grade_8.get('id', str(grade_8['_id']))
    print(f"Grade 8 ID: {grade_8_id[:20]}...")
    
    total_strands = 0
    total_substrands = 0
    total_slos = 0
    total_activities = 0
    
    # Seed all subjects
    subjects_to_seed = [
        MATHEMATICS_GRADE_8,
        INTEGRATED_SCIENCE_GRADE_8,
        SOCIAL_STUDIES_GRADE_8,
        ENGLISH_GRADE_8,
        KISWAHILI_GRADE_8,
    ]
    
    for subject_data in subjects_to_seed:
        s, ss, slo, act = await seed_subject_complete(subject_data, grade_8_id)
        total_strands += s
        total_substrands += ss
        total_slos += slo
        total_activities += act
    
    print("\n" + "=" * 70)
    print("SEEDING COMPLETE")
    print("=" * 70)
    print(f"Total Strands Added: {total_strands}")
    print(f"Total Substrands Added: {total_substrands}")
    print(f"Total SLOs Added: {total_slos}")
    print(f"Total Activity Sets Added: {total_activities}")
    
    # Verify database totals
    print("\n=== Database Totals ===")
    print(f"  Grades: {await db.grades.count_documents({})}")
    print(f"  Subjects: {await db.subjects.count_documents({})}")
    print(f"  Strands: {await db.strands.count_documents({})}")
    print(f"  Substrands: {await db.substrands.count_documents({})}")
    print(f"  SLOs: {await db.slos.count_documents({})}")
    print(f"  Learning Activities: {await db.learning_activities.count_documents({})}")


if __name__ == "__main__":
    asyncio.run(main())
