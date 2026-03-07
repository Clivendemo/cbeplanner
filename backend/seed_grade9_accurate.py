#!/usr/bin/env python3
"""
Accurate Grade 9 Curriculum Seeding Script
==========================================
This script seeds Grade 9 curriculum data extracted DIRECTLY from KICD PDFs.
All content is taken verbatim from the official curriculum design documents.

Subjects covered:
1. Mathematics (GRADE.9.MATHEMATICS.pdf)
2. English (GRADE.9.ENGLISH.pdf)
3. Integrated Science (GRADE.9.INTEGRATED.SCIENCE.pdf)
4. Kiswahili (Kiswahili-Grade-9.pdf)
5. Social Studies (Social-Studies-Grade-9-Design-Formatted-April-2024.pdf)

IMPORTANT: This script links to EXISTING subjects - does NOT create duplicates.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
db_name = os.environ.get('DB_NAME', 'cbeplanner')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


# ============================================================================
# MATHEMATICS GRADE 9 - Extracted from GRADE.9.MATHEMATICS.pdf
# ============================================================================
MATHEMATICS_GRADE_9 = {
    "name": "Mathematics",
    "strands": [
        {
            "name": "Numbers",
            "substrands": [
                {
                    "name": "Integers",
                    "slos": [
                        {"name": "perform basic operations on Integers in different situations"},
                        {"name": "work out combined Operations on Integers in different situations"},
                        {"name": "apply Integers to real life situations"},
                        {"name": "use IT or other resources to learn more on integers"},
                        {"name": "appreciate use of integers in real life situations"},
                    ],
                    "learning_experiences": [
                        "discuss and work out basic operations on integers using number cards and charts",
                        "Play games involving numbers and operations. Pick integers and perform all basic operations",
                        "work out combined operations of integers in the correct order",
                        "carry out activities such as reading temperature changes in a thermometer and discuss how to record it",
                        "use IT and other resources such as print to carry out operations on integers",
                        "play creative games that involve integers"
                    ],
                    "inquiry_questions": ["How do we carry out operations of integers in real life situations?", "How do we apply integers in daily activities?"],
                    "core_competencies": ["Critical thinking and problem solving- interpretation and inference", "Learning to learn- organizing own learning", "Digital literacy- interacting with technologies"],
                    "values": ["Respect", "Unity"],
                    "pcis": ["Environmental education"]
                },
                {
                    "name": "Cubes and Cube Roots",
                    "slos": [
                        {"name": "Work out cubes of numbers by multiplication in real life situations"},
                        {"name": "Determine cubes of numbers from mathematical tables in different situations"},
                        {"name": "Determine cube roots of numbers by factor method in different situations"},
                        {"name": "Determine cube roots of numbers from mathematical tables in different situations"},
                        {"name": "Apply cubes and cube roots in real life situations"},
                        {"name": "Work out cubes and cube roots using IT devices"},
                    ],
                    "learning_experiences": [
                        "use stacks of cubes to demonstrate the concept of cube and cube roots",
                        "demonstrate stacking of cubes",
                        "discuss the volume of a cube and determine both the cube and cube root and relate the two",
                        "read the cube of numbers from mathematical tables and relate to cube roots",
                        "use IT devices to determine cube and cube roots of numbers"
                    ],
                    "inquiry_questions": ["How do we work out the cubes of numbers?", "How do we work out the cube roots of numbers?", "Where do we apply cubes and cube roots in real life situations?"],
                    "core_competencies": ["Communication and collaboration- speaking and listening", "Imagination and creativity- open mindedness and creativity"],
                    "values": ["Respect"],
                    "pcis": []
                },
                {
                    "name": "Indices and Logarithms",
                    "slos": [
                        {"name": "Express numbers in index form in different situations"},
                        {"name": "Generate the laws of Indices in different situations"},
                        {"name": "Apply the laws of indices in different situations"},
                        {"name": "Relate Powers of 10 to common logarithms in different situations"},
                        {"name": "Use IT to learn more on indices and common logarithms"},
                        {"name": "Appreciate use of indices and logarithms in real life situations"},
                    ],
                    "learning_experiences": [
                        "discuss indices and identify the base",
                        "show the laws of indices using multiplication and division",
                        "use the laws of indices to work out indices",
                        "discuss and relate powers of 10 to common logarithms",
                        "use IT to work out common logarithms or use mathematical tables"
                    ],
                    "inquiry_questions": ["How do we express numbers in powers?"],
                    "core_competencies": ["Critical thinking and problem solving", "Self-efficacy"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Self-awareness"]
                },
                {
                    "name": "Compound Proportions and Rates of Work",
                    "slos": [
                        {"name": "divide quantities into proportional parts in real life situations"},
                        {"name": "relate different ratios in real life situations"},
                        {"name": "work out compound proportions using ratio method in different situations"},
                        {"name": "calculate rates of work in real life situations"},
                    ],
                    "learning_experiences": [
                        "discuss and divide quantities into proportional parts and express as a fraction",
                        "compare and write different ratios",
                        "determine compound proportions using ratios",
                        "work out rates of work",
                        "play games on rates of work using IT devices"
                    ],
                    "inquiry_questions": ["What are proportions?", "Why do we work fast?"],
                    "core_competencies": ["Citizenship- active community life skills", "Critical thinking and problem solving- interpretation and inference"],
                    "values": ["Responsibility", "Respect for self and others"],
                    "pcis": ["Self-esteem"]
                },
            ]
        },
        {
            "name": "Algebra",
            "substrands": [
                {
                    "name": "Matrices",
                    "slos": [
                        {"name": "identify a matrix in different situations"},
                        {"name": "determine the order of a matrix in different situations"},
                        {"name": "determine the position of items in a matrix in different situations"},
                        {"name": "determine compatibility of matrices in addition and subtraction"},
                        {"name": "carry out addition and subtraction of matrices in real life situations"},
                        {"name": "reflect on the use of matrices in real life situations"},
                    ],
                    "learning_experiences": [
                        "discuss the use of tables such as football league tables, travel schedules, shopping lists",
                        "arrange items in rows and columns and discuss how to represent a matrix",
                        "organize objects in rows and columns and give the order of the matrix",
                        "discuss and identify the position of each item or element in terms of row and column",
                        "discuss and identify matrices that have equal number of rows and columns for compatibility",
                        "discuss and note what is represented by the rows and columns from two or more matrices"
                    ],
                    "inquiry_questions": ["How do we use matrices in real life situations?"],
                    "core_competencies": ["Communication and collaboration", "Learning to learn"],
                    "values": ["Integrity"],
                    "pcis": ["Social and economic issues", "Citizenship"]
                },
                {
                    "name": "Equations of a Straight Line",
                    "slos": [
                        {"name": "identify the gradient in real life situations"},
                        {"name": "determine the gradient of a line from two known points"},
                        {"name": "determine the equation of a straight line given two points"},
                        {"name": "determine the equation of a straight line from a known point and a gradient"},
                        {"name": "express the equation of a straight line in the form of y = mx + c"},
                        {"name": "interpret the equation y = mx + c in different situations"},
                        {"name": "determine the x and y intercepts of a straight line"},
                        {"name": "recognize the use of equations of straight lines in real life"},
                    ],
                    "learning_experiences": [
                        "discuss steepness in relation to gradient from the immediate environment",
                        "incline a ladder at different positions on the wall to demonstrate change in steepness",
                        "observe and climb up and down places such as the stairs or hills and relate to gradients",
                        "work out the equation of a straight line given two points or given a point and a gradient",
                        "discuss and rewrite the equation of a straight line as y = mx + c",
                        "work out the value of x when y is zero and the value of y when x is zero",
                        "use IT or other resources to show different hills and mountains and discuss steepness"
                    ],
                    "inquiry_questions": ["How do we use gradient or steepness in our daily activities?"],
                    "core_competencies": ["Digital literacy", "Learning to learn"],
                    "values": ["Integrity"],
                    "pcis": ["Safety"]
                },
                {
                    "name": "Linear Inequalities",
                    "slos": [
                        {"name": "solve linear inequalities in one unknown"},
                        {"name": "represent linear inequalities in one unknown graphically"},
                        {"name": "represent linear inequality in two unknowns graphically"},
                        {"name": "apply linear inequalities to real life situations"},
                        {"name": "reflect on the use of linear inequalities in real life"},
                    ],
                    "learning_experiences": [
                        "discuss why sometimes resources are shared unequally",
                        "discuss simple inequality statements, form and work out the inequalities in one unknown",
                        "discuss and generate a table of values and draw linear inequalities in one unknown",
                        "discuss and generate a table of values and draw linear inequalities in two unknowns",
                        "discuss and work out linear inequalities that involve real life cases",
                        "use IT or other graphing tools to present linear inequalities"
                    ],
                    "inquiry_questions": ["How do we represent linear inequalities in graphs?", "How do we use linear inequalities in real life situations?"],
                    "core_competencies": ["Digital literacy", "Communication and collaboration"],
                    "values": ["Social justice"],
                    "pcis": ["Citizenship"]
                },
            ]
        },
        {
            "name": "Measurements",
            "substrands": [
                {
                    "name": "Area",
                    "slos": [
                        {"name": "calculate the area of a pentagon and a hexagon in different situations"},
                        {"name": "work out the surface area of triangular and rectangular based prisms"},
                        {"name": "work out the surface area of triangular, rectangular and square based pyramids"},
                        {"name": "calculate the area of a sector and segment of a circle"},
                        {"name": "work out the surface area of a cone in real life situations"},
                        {"name": "calculate the surface area of a sphere in real life situations"},
                        {"name": "recognize the use of area in real life situations"},
                    ],
                    "learning_experiences": [
                        "discuss the properties of regular polygons and use cut outs to work out the area of pentagons and hexagons",
                        "collect from the environment objects that are spheres, cones/funnels, pyramids, prisms and frustums",
                        "discuss and sketch the nets of the solids",
                        "use models of prisms to work out the surface area of prisms",
                        "open up the net and draw the faces of a pyramid",
                        "draw a circle with a sector, a chord and a segment",
                        "open the cone to form a net and determine the curved surface area",
                        "use relevant formulas to work out the surface area of different sizes of spherical balls",
                        "use IT or other resources to sketch different models and nets"
                    ],
                    "inquiry_questions": ["How do we determine the area of different surfaces?"],
                    "core_competencies": ["Communication and collaboration", "Creativity and imagination"],
                    "values": ["Responsibility"],
                    "pcis": ["Patriotism"]
                },
                {
                    "name": "Volume of Solids",
                    "slos": [
                        {"name": "work out the volume of a triangular and rectangular based prisms"},
                        {"name": "calculate the volume of a triangular, rectangular and squares based pyramids"},
                        {"name": "work out the volume of a cone in real life situations"},
                        {"name": "determine the volume of a frustum in real life situations"},
                        {"name": "calculate the volume of a sphere in real life situations"},
                        {"name": "promote use of volume and capacity of different containers in real life situations"},
                    ],
                    "learning_experiences": [
                        "collect different containers and objects including prisms, pyramids, cones, funnels and balls",
                        "identify and discuss the model of a prism and determine the volume",
                        "use relevant formulae to work out the volume of pyramids and cones",
                        "identify and work out the volume of models of a pyramid",
                        "Cut the pyramid into two parts to get a frustum and determine the volume",
                        "Play any games involving different sizes of balls and work out volume of a sphere",
                        "use IT or other resources to determine the volumes of solids"
                    ],
                    "inquiry_questions": ["How do we determine the volume of different solids?", "How do we use the volume of solids in real life situations?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and Imagination"],
                    "values": ["Responsibility"],
                    "pcis": ["Environmental Education", "Safety"]
                },
                {
                    "name": "Mass, Volume, Weight and Density",
                    "slos": [
                        {"name": "convert units of mass from one form to another in different situations"},
                        {"name": "relate mass and weight in real life situations"},
                        {"name": "determine mass, volume and density in different situations"},
                        {"name": "apply density to real life situations"},
                        {"name": "recognize the use of density in daily life"},
                    ],
                    "learning_experiences": [
                        "discuss different instruments and tools used in weighing materials or objects",
                        "Collect and weigh different materials or objects and change one unit of mass to another",
                        "discuss the relationship between mass and weight",
                        "carry out activities relating mass and volume to density using containers",
                        "discuss and find the density of different materials or objects",
                        "work out mass, volume and density using IT or other resources"
                    ],
                    "inquiry_questions": ["How do you weigh materials and objects?"],
                    "core_competencies": ["Communication and collaboration", "Creativity and imagination", "Digital literacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Education for Sustainable Development (ESD)", "Self-awareness"]
                },
                {
                    "name": "Time, Distance and Speed",
                    "slos": [
                        {"name": "work out speed in km/h and m/s in real life situations"},
                        {"name": "work out average speed in real life situations"},
                        {"name": "determine velocity in real life situations"},
                        {"name": "work out acceleration in real life situations"},
                        {"name": "identify the longitudes on the globe"},
                        {"name": "relate longitudes to time on the globe"},
                        {"name": "determine local time of places on the earth along different longitudes"},
                        {"name": "appreciate use of time and distance in real life situations"},
                    ],
                    "learning_experiences": [
                        "engage in activities that involve measuring distances and time, for example running track events",
                        "discuss and relate distance and time",
                        "discuss the difference between velocity and speed",
                        "Discuss and determine acceleration from track events in school or community",
                        "discuss and use maps and models of a globe to work out time of different places",
                        "use IT devices to watch videos on the globe, longitudes and time zones",
                        "use other resources such as maps to locate different places on the earth"
                    ],
                    "inquiry_questions": ["How do we observe speed in daily activities?", "Why does time vary in different places of the world?"],
                    "core_competencies": ["Self-efficacy", "Digital literacy", "Citizenship- global citizenship"],
                    "values": ["Integrity", "Respect"],
                    "pcis": ["Safety", "Education for Sustainable Development (ESD)", "Self-awareness"]
                },
                {
                    "name": "Money",
                    "slos": [
                        {"name": "identify currencies that are used in different countries"},
                        {"name": "convert currency from one form to another in real life situations"},
                        {"name": "work out import and export duties charged on goods and services"},
                        {"name": "work out excise duty charged on goods and services"},
                        {"name": "determine value added tax charged on goods and services"},
                        {"name": "appreciate use of money in day to day activities"},
                    ],
                    "learning_experiences": [
                        "use IT or other resources to obtain currencies from different countries",
                        "work out currency exchange from Kenya Shillings to any other currency and vice versa",
                        "discuss and determine the export and import duty charges on different goods",
                        "discuss and identify goods that attract excise duty",
                        "use receipts from shopping to discuss and work out VAT on goods and services",
                        "identify currency exchange rates from different sources"
                    ],
                    "inquiry_questions": ["Why do we change currencies from one form to another?", "What are the types of taxes the government levy on its citizens?"],
                    "core_competencies": ["Global Citizenship", "Digital Literacy"],
                    "values": ["Integrity", "Social Cohesion"],
                    "pcis": ["Financial Literacy", "Education for Sustainable Development (ESD)"]
                },
                {
                    "name": "Approximations and Errors",
                    "slos": [
                        {"name": "approximate quantities in measurements in different situations"},
                        {"name": "determine errors using estimations and actual measurements of quantities"},
                        {"name": "determine percentage errors using actual measurements of quantities"},
                        {"name": "appreciate approximations and errors in real life situations"},
                    ],
                    "learning_experiences": [
                        "carryout activities of measurements of different quantities using arbitrary units",
                        "Estimate and measure different quantities using appropriate instruments",
                        "compare the estimates and the actual measurements and determine the error",
                        "work out the percentage error from the estimated and the actual measurements",
                        "work out errors using IT devices or other resources"
                    ],
                    "inquiry_questions": ["How do we estimate measurements of different quantities?"],
                    "core_competencies": ["Creativity and imagination", "Digital literacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Safety"]
                },
            ]
        },
        {
            "name": "Geometry",
            "substrands": [
                {
                    "name": "Coordinates and Graphs",
                    "slos": [
                        {"name": "plot out points on a Cartesian plane"},
                        {"name": "draw a straight line graph given an equation"},
                        {"name": "draw parallel lines on the Cartesian plane"},
                        {"name": "relate the gradients of parallel lines"},
                        {"name": "draw perpendicular lines on the Cartesian plane"},
                        {"name": "relate the gradients of perpendicular lines"},
                        {"name": "apply graphs of straight line in real life situation"},
                    ],
                    "learning_experiences": [
                        "work in groups and locate the point of intersection of the x coordinate and the y- coordinates",
                        "generate a table of values from equation of a straight line, plot and join the points",
                        "Generate table of values for each equation, plot and join them to form straight lines",
                        "work out the gradients of each of the lines and compare them to establish parallelism",
                        "Generate table of values for perpendicular lines, plot and join them",
                        "work out the gradients to establish the relationship of perpendicular lines"
                    ],
                    "inquiry_questions": ["How do we draw graphs of straight lines?", "How do we interpret graphs of straight lines?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving"],
                    "values": ["Responsibility"],
                    "pcis": ["Education for Sustainable Development (ESD)", "Safety"]
                },
                {
                    "name": "Scale Drawing",
                    "slos": [
                        {"name": "identify compass and true bearings in real life situations"},
                        {"name": "determine the bearing of one point from another in real life situations"},
                        {"name": "locate a point using bearing and distance in real life situations"},
                        {"name": "identify angles of elevation in real life situations"},
                        {"name": "determine angles of elevation in different situations"},
                        {"name": "identify angles of depression in real life situations"},
                        {"name": "determine angles of depression in different situations"},
                        {"name": "apply scale drawing in simple surveying"},
                        {"name": "appreciate the use of scale drawing in real life situations"},
                    ],
                    "learning_experiences": [
                        "draw and discuss the compass directions and relate to the compass and true North bearings",
                        "discuss and locate places from different points using bearings",
                        "discuss and locate a place using bearing and distance",
                        "Sketch and use scale drawing to show the position of places",
                        "carryout activities involving angles of elevation",
                        "Carryout activities involving angles of depression",
                        "discuss, sketch and make a scale drawing to determine the angles",
                        "discuss and use scale drawing in simple surveying",
                        "observe maps or watch videos on bearings and simple surveying"
                    ],
                    "inquiry_questions": ["How do we use scale drawing in real life?"],
                    "core_competencies": ["Creativity and imagination", "Citizenship"],
                    "values": ["Unity", "Social Cohesion"],
                    "pcis": ["Careers in scale drawing and surveying"]
                },
                {
                    "name": "Similarity and Enlargement",
                    "slos": [
                        {"name": "identify similar figures and their properties"},
                        {"name": "draw similar figures in different situations"},
                        {"name": "determine properties of enlargement of different figures"},
                        {"name": "apply properties of enlargement to draw similar objects and their images"},
                        {"name": "determine the linear scale factor of similar figures"},
                        {"name": "promote use of similarity and enlargement in real life situations"},
                    ],
                    "learning_experiences": [
                        "collect objects and sort according to similarity",
                        "use properties of similar objects to scale-draw similar figures",
                        "discuss and identify properties of enlargement",
                        "use properties of enlargement to represent objects and their images",
                        "determine the linear relationship of similar figures and objects",
                        "enlarge objects and figures using IT devices"
                    ],
                    "inquiry_questions": ["What are similar objects?", "How do we use enlargement in real life situations?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Social cohesion"],
                    "pcis": ["Environmental Education"]
                },
                {
                    "name": "Trigonometry",
                    "slos": [
                        {"name": "identify angles and sides of right angled triangles in different situations"},
                        {"name": "identify Sine, Cosine and Tangent ratios from a right angled triangle"},
                        {"name": "read tables of trigonometric ratios for acute angles"},
                        {"name": "determine trigonometric ratios of acute angles using calculators"},
                        {"name": "apply trigonometric ratios to calculate lengths and angles"},
                        {"name": "appreciate use of trigonometric ratios in real life situations"},
                    ],
                    "learning_experiences": [
                        "draw right angled triangles and recognize angles and sides",
                        "discuss the relationship between angles and sides",
                        "discuss and relate the trigonometric ratios to angles",
                        "use trigonometric ratios to determine lengths and angles",
                        "use Mathematical tables or IT devices to find trigonometric ratios"
                    ],
                    "inquiry_questions": ["What is the relationship between angles and sides in a right angled triangle?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility"],
                    "pcis": ["Safety"]
                },
            ]
        },
        {
            "name": "Data Handling and Probability",
            "substrands": [
                {
                    "name": "Data Interpretation (Grouped Data)",
                    "slos": [
                        {"name": "determine appropriate class width for grouping data"},
                        {"name": "draw frequency distribution tables of grouped data"},
                        {"name": "identify the modal class of grouped data"},
                        {"name": "calculate the mean of a grouped data from real life situations"},
                        {"name": "determine the median of a grouped data from real life situations"},
                        {"name": "appreciate data interpretation in real life situations"},
                    ],
                    "learning_experiences": [
                        "collect data and work out an appropriate class width",
                        "tally the data and represent it in a frequency distribution table",
                        "recognize the modal class from a set of grouped data",
                        "work out the mean from different sets of grouped data",
                        "use the frequencies to determine the median class",
                        "work out the median from different sets of grouped data",
                        "use IT or other materials to determine the mean and median"
                    ],
                    "inquiry_questions": ["How do we interpret data?"],
                    "core_competencies": ["Learning to learn", "Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Respect"],
                    "pcis": ["Citizenship"]
                },
                {
                    "name": "Probability",
                    "slos": [
                        {"name": "perform experiments involving equally and likely outcomes in different situations"},
                        {"name": "determine the range of probability of an event"},
                        {"name": "identify mutually exclusive events in real life situations"},
                        {"name": "perform experiments of single chance involving mutually exclusive events"},
                        {"name": "perform experiments involving independent events in different situations"},
                        {"name": "draw a tree diagram for a single outcome"},
                        {"name": "appreciate the probability of events occurring in real life situations"},
                    ],
                    "learning_experiences": [
                        "discuss and carry out experiments of events involving equally and likely outcomes",
                        "work out the range of probability of different events",
                        "discuss and carry out experiments involving mutually inclusive events",
                        "discuss and carry out experiments involving independent events",
                        "practice representing probability occurrences in a tree diagram",
                        "use IT or other resources to explore more on probability"
                    ],
                    "inquiry_questions": ["Why is probability important in real life situations?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving", "Self- efficacy"],
                    "values": ["Responsibility", "Social cohesion"],
                    "pcis": ["Financial Literacy"]
                },
            ]
        },
    ]
}


# ============================================================================
# INTEGRATED SCIENCE GRADE 9 - Extracted from GRADE.9.INTEGRATED.SCIENCE.pdf
# ============================================================================
INTEGRATED_SCIENCE_GRADE_9 = {
    "name": "Integrated Science",
    "strands": [
        {
            "name": "Mixtures, Elements and Compounds",
            "substrands": [
                {
                    "name": "Structure of the atom",
                    "slos": [
                        {"name": "describe the structure of the atom"},
                        {"name": "determine the mass number of elements"},
                        {"name": "draw the electron arrangement in atoms using dot or cross diagrams"},
                        {"name": "classify elements into metals and non-metals"},
                        {"name": "show interest in classifying elements into metals and non-metals"},
                    ],
                    "learning_experiences": [
                        "discuss the meaning of the atom and illustrate its structure",
                        "work out the mass number of an element with peers",
                        "write the electron arrangements of elements",
                        "illustrate the electron arrangement in atoms using dot or cross diagrams collaboratively",
                        "use electron arrangement to classify elements into metals and non-metals",
                        "use digital media to observe animations or videos on the structure of an atom",
                        "Project: model the atomic structure of selected elements using locally available materials"
                    ],
                    "inquiry_questions": ["How is the structure of the atom important?"],
                    "core_competencies": ["Communication and collaboration", "Creativity and imagination"],
                    "values": ["Unity", "Integrity"],
                    "pcis": ["Socio-economic issues (cyber security)"]
                },
                {
                    "name": "Metals and Alloys",
                    "slos": [
                        {"name": "describe the physical properties of metals"},
                        {"name": "describe the composition of alloys"},
                        {"name": "identify the uses of metals and alloys in day to day life"},
                        {"name": "explain the effects of rusting of metals"},
                        {"name": "appreciate the importance of common alloys in day to day life"},
                    ],
                    "learning_experiences": [
                        "identify metals and non-metals in their environment",
                        "carry out experiments to demonstrate the physical properties of metals",
                        "discuss the composition of common alloys with peers",
                        "identify some items from the locality that have been made from alloys",
                        "discuss the uses of common metals and alloys",
                        "discuss causes, effects and ways of controlling rusting of metals",
                        "use digital or print media to search for information on physical properties of metals and alloys"
                    ],
                    "inquiry_questions": ["How are alloys important in day-day life?"],
                    "core_competencies": ["Communication and collaboration", "Digital literacy", "Financial Literacy"],
                    "values": ["Respect", "Peace"],
                    "pcis": []
                },
                {
                    "name": "Water hardness",
                    "slos": [
                        {"name": "describe the physical properties of water"},
                        {"name": "distinguish between hard and soft water in nature"},
                        {"name": "apply methods of softening hard water in day to day life"},
                        {"name": "outline advantages and disadvantages of hard and soft water"},
                        {"name": "appreciate the applications of soft and hard water in day to day life"},
                    ],
                    "learning_experiences": [
                        "Collect and observe water from different sources, compare in terms of appearance, odour, taste and boiling point",
                        "carry out activities to compare the lathering abilities of various samples of water with soap",
                        "group the samples into hard and soft water",
                        "explain the meaning of hard and soft water",
                        "discuss the advantages and disadvantages of soft and hard water",
                        "perform various activities for softening hard water",
                        "use digital or print media to search for information on methods of softening hard water"
                    ],
                    "inquiry_questions": ["What is the importance of different types of water?", "Why is hard water preferred for drinking?"],
                    "core_competencies": ["Learning to learn", "Critical thinking and problem solving"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Financial literacy"]
                },
            ]
        },
        {
            "name": "Living Things and Their Environment",
            "substrands": [
                {
                    "name": "Nutrition in plants",
                    "slos": [
                        {"name": "identify external and internal parts of a leaf"},
                        {"name": "explain adaptations of the leaf to photosynthesis"},
                        {"name": "describe the process of photosynthesis"},
                        {"name": "investigate the conditions necessary for photosynthesis"},
                        {"name": "appreciate the process of photosynthesis in nature"},
                    ],
                    "learning_experiences": [
                        "use a hand lens to observe fresh leaves of plants, draw and label the external parts",
                        "use print or non-print media to search for information on the internal structure of the leaf",
                        "discuss the adaptations of a leaf in relation to their roles in photosynthesis",
                        "observe the structure of the chloroplast on charts/photomicrographs",
                        "use print or non-print media to search for information on the process and products of photosynthesis",
                        "use print or non-print media to search for information on conditions necessary for photosynthesis",
                        "set-up experiments to show that light, carbon (IV) oxide and chlorophyll are necessary for photosynthesis"
                    ],
                    "inquiry_questions": ["What is the importance of photosynthesis in nature?"],
                    "core_competencies": ["Learning to learn", "Self-efficacy"],
                    "values": ["Social justice", "Integrity"],
                    "pcis": ["Environmental conservation", "Safety"]
                },
                {
                    "name": "Nutrition in animals",
                    "slos": [
                        {"name": "outline modes of nutrition in animals"},
                        {"name": "describe the structure and functions of different types of teeth"},
                        {"name": "classify animals based on their dentition"},
                        {"name": "describe the process of digestion in human beings"},
                        {"name": "appreciate that animals have varied modes of nutrition"},
                    ],
                    "learning_experiences": [
                        "use print or non-print media to search for information on modes of nutrition in animals",
                        "use specimens/charts/models/digital media to identify and draw different types of teeth",
                        "collaboratively discuss the functions of different types of teeth",
                        "use specimens/charts/models/digital media to study dentition in different animals",
                        "use print or non-print media to search for information on the process of digestion in human beings"
                    ],
                    "inquiry_questions": ["How do different animals feed?", "How is food digested in the human body?"],
                    "core_competencies": ["Communication and Collaboration"],
                    "values": ["Unity", "Respect"],
                    "pcis": ["Animal welfare"]
                },
                {
                    "name": "Reproduction in plants",
                    "slos": [
                        {"name": "outline functions of parts of a flower"},
                        {"name": "describe pollination in plants"},
                        {"name": "outline the adaptations of flowers to wind and insect pollination"},
                        {"name": "explain fertilisation and fruit formation in flowering plants"},
                        {"name": "categorise fruits and seeds based on their mode of dispersal"},
                        {"name": "recognize the role of flowers in nature"},
                    ],
                    "learning_experiences": [
                        "collaboratively discuss the functions of parts of a flower",
                        "use print or non-print media to search for information on meaning and types of pollination",
                        "use print or non-print media to search for information on adaptations of flowers to pollination",
                        "study samples of flowers to discuss their adaptations to agents of pollination",
                        "watch animations or take an excursion to observe pollinating agents in action",
                        "use print or print media to search for information on effects of agrochemicals on pollinating agents",
                        "use print and non-print media to search for information on fertilisation and fruit formation",
                        "collaboratively study illustrations/animations on fertilisation, seed and fruit formation",
                        "use print and non-print media to search for information on seeds and fruits dispersal in plants",
                        "observe different fruits and seeds and categorise them based on their mode of dispersal",
                        "discuss the importance of fruit and seed dispersal"
                    ],
                    "inquiry_questions": ["How does reproduction in plants occur?"],
                    "core_competencies": ["Learning to learn", "Digital literacy"],
                    "values": ["Social Justice"],
                    "pcis": ["Biodiversity", "Safety and Security"]
                },
                {
                    "name": "The interdependence of life",
                    "slos": [
                        {"name": "explain the biotic and abiotic factors of the environment"},
                        {"name": "construct food chains and food webs in the environment"},
                        {"name": "describe the effect of human activities on the environment"},
                        {"name": "appreciate the interdependence between living and non-living factors of the environment"},
                    ],
                    "learning_experiences": [
                        "use print and non-print material to search for information biotic interrelationships",
                        "investigate the interrelationships between biotic factors of the environment in their locality",
                        "observe videos or animations showing the interrelationships between biotic factors",
                        "use print and non-print media to search for information on Kenya national parks and game reserves",
                        "discuss the effect of abiotic factors on living organisms",
                        "search for information on the effect of human activities on the environment",
                        "carry out activities to identify living organisms and what they feed on",
                        "construct food chains and food webs",
                        "discuss the role of decomposers in an ecosystem and their importance in recycling nutrients"
                    ],
                    "inquiry_questions": ["What is the role of living and non-living factors in environments?"],
                    "core_competencies": ["Citizenship", "Critical thinking and problem solving"],
                    "values": ["Patriotism", "Peace"],
                    "pcis": ["Environmental conservation"]
                },
            ]
        },
        {
            "name": "Force and Energy",
            "substrands": [
                {
                    "name": "Curved mirrors",
                    "slos": [
                        {"name": "describe types of curved mirrors"},
                        {"name": "draw ray diagrams to locate images formed by concave and convex mirrors"},
                        {"name": "describe the characteristics of images formed by concave and convex mirrors"},
                        {"name": "explain the uses of concave and convex mirrors in day to day life"},
                        {"name": "appreciate the applications of curved mirrors in day to day life"},
                    ],
                    "learning_experiences": [
                        "discuss the types of curved mirrors (concave, convex and parabolic surfaces)",
                        "discuss with peers the terms used in curved mirrors (aperture, pole, centre of curvature, etc.)",
                        "carry out activities to locate position of images formed by concave and convex mirrors",
                        "illustrate image positions for various object positions",
                        "discuss the characteristics of images formed by curved mirrors",
                        "discuss the applications of concave and convex mirrors in day to day life",
                        "use digital or print media to explore more information on applications of curved mirrors"
                    ],
                    "inquiry_questions": ["How are curved mirrors used in day to day life?"],
                    "core_competencies": ["Self-efficacy", "Communication and Collaboration"],
                    "values": ["Social justice", "Responsibility"],
                    "pcis": ["Socio-economic issues"]
                },
                {
                    "name": "Waves",
                    "slos": [
                        {"name": "describe generation of waves in nature"},
                        {"name": "classify waves as longitudinal and transverse"},
                        {"name": "describe basic characteristic of waves in nature"},
                        {"name": "describe remote sensing in relation to waves"},
                        {"name": "describe applications of waves in day to day life"},
                        {"name": "appreciate the applications of waves in day to day life"},
                    ],
                    "learning_experiences": [
                        "brainstorm on the meaning of wave as used in science",
                        "carry out activities to demonstrate generation of waves in nature",
                        "classify waves into longitudinal and transverse",
                        "Carry out activities to demonstrate the parts of a wave",
                        "carry out activities in groups to demonstrate characteristics of waves",
                        "discuss remote sensing in relation to waves",
                        "use digital or print media to search for more information on remote sensing and waves",
                        "discuss the applications of waves in real life situations"
                    ],
                    "inquiry_questions": ["How are waves applied in our day to day life?"],
                    "core_competencies": ["Learning to learn", "Creativity and Imagination"],
                    "values": ["Respect", "Peace"],
                    "pcis": ["Learner support programs"]
                },
            ]
        },
    ]
}


# ============================================================================
# SOCIAL STUDIES GRADE 9 - Extracted from Social-Studies-Grade-9-Design.pdf
# ============================================================================
SOCIAL_STUDIES_GRADE_9 = {
    "name": "Social Studies",
    "strands": [
        {
            "name": "Social Studies and Career Development",
            "substrands": [
                {
                    "name": "Pathway Choices",
                    "slos": [
                        {"name": "identify factors to consider in the selection of a pathway"},
                        {"name": "examine requirements for Social sciences pathway at senior school"},
                        {"name": "choose a possible track within a pathway at senior school"},
                        {"name": "appreciate the need for choosing a pathway in senior school"},
                    ],
                    "learning_experiences": [
                        "brainstorm the meaning of a career path",
                        "engage a resource person to discuss factors to consider in the selection of a pathway",
                        "use digital devices/print materials to examine requirements for social science pathway",
                        "create and display charts with pathways and their respective requirements",
                        "create and display posters on pathways using locally available resources",
                        "choose and journal possible tracks in a given pathway for academic growth",
                        "compose and recite poems on pathway choices"
                    ],
                    "inquiry_questions": ["Why is it important to learn about career paths?"],
                    "core_competencies": ["Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": ["Career Guidance"]
                },
                {
                    "name": "Pre-career Support systems",
                    "slos": [
                        {"name": "explore and use support systems for pre-career and other needs"},
                        {"name": "analyze challenges arising from existing support systems for pre-career and other needs"},
                        {"name": "design solutions to challenges arising from support systems"},
                        {"name": "explain the significance of pre-career mapping for individual growth"},
                        {"name": "appreciate the value of the pre-career support systems"},
                    ],
                    "learning_experiences": [
                        "using digital or printed materials search for the meaning and examples of support systems",
                        "brainstorm on effective use of different support systems in the community",
                        "engage a resource person to discuss significance of pre-career mapping",
                        "brainstorm on challenges arising from involvement in existing pre-career support systems",
                        "search for solutions to challenges arising from existing pre-career support systems",
                        "compose and recite poems highlighting the value of pre-career support system"
                    ],
                    "inquiry_questions": ["Why does a learner need pre-career support?"],
                    "core_competencies": ["Creativity and Imagination"],
                    "values": ["Responsibility"],
                    "pcis": ["Career Guidance"]
                },
            ]
        },
        {
            "name": "Community Service-Learning",
            "substrands": [
                {
                    "name": "Community Service Learning Project",
                    "slos": [
                        {"name": "identify a problem in the community"},
                        {"name": "design a solution to the identified problem"},
                        {"name": "plan to solve the identified problem in the community"},
                        {"name": "implement the plan to solve the problem"},
                        {"name": "write a report on the concluded project"},
                        {"name": "appreciate teamwork in addressing community problems"},
                    ],
                    "learning_experiences": [
                        "brainstorm and identify problems/gaps/opportunities in their class/school/community",
                        "discuss and adapt one identified problem for the class/group project",
                        "authenticate the problem/gap and write down the statement of the problem",
                        "search, discuss and agree on an appropriate solution/way forward",
                        "discuss a plan of implementing the proposed solution",
                        "implement the plan prudently to address the identified problem",
                        "reflect on the concluded project and submit a summary report",
                        "reflect on the whole process and the lessons learnt"
                    ],
                    "inquiry_questions": ["What does one consider while implementing a project?", "Why is reflection important in a project?"],
                    "core_competencies": ["Communication and collaboration", "Self-efficacy", "Creativity and imagination", "Critical thinking and problem-solving", "Digital literacy", "Learning to learn", "Citizenship"],
                    "values": ["Social justice", "Unity"],
                    "pcis": ["Governance", "Critical thinking skills"]
                },
            ]
        },
        {
            "name": "People and Relationships",
            "substrands": [
                {
                    "name": "Socio-Economic Practices of Early Humans",
                    "slos": [
                        {"name": "describe the socio-economic practices of early humans in Africa during the Stone Age period"},
                        {"name": "examine different types of tools used by early humans during the Stone Age period"},
                        {"name": "illustrate the tools used by early humans during the Stone Age period"},
                        {"name": "recognise socio-economic practices of the early humans"},
                    ],
                    "learning_experiences": [
                        "interact with digital technology or print media to research on socio-economic practices",
                        "brainstorm on socio-economic practices of early humans during the Stone Age period",
                        "debate on the relevance of socio-economic practices of early humans to modern society",
                        "discuss the various types of tools used by early humans during the Stone Age period",
                        "use digital resources to view various types of tools used by early humans",
                        "draw various types of tools used by early humans",
                        "engage a resource person to discuss why Africa is regarded as the birth place of human technology"
                    ],
                    "inquiry_questions": ["How do socio-economic practices of early humans impact on the modern society?"],
                    "core_competencies": ["Digital literacy", "Creativity and imagination"],
                    "values": ["Responsibility", "Unity", "Respect"],
                    "pcis": ["Social cohesion", "Effective communication"]
                },
                {
                    "name": "Indigenous Knowledge systems in African Societies",
                    "slos": [
                        {"name": "identify types of indigenous knowledge systems in African societies for self-identity"},
                        {"name": "explain how the indigenous knowledge systems were used for sustainability of life"},
                        {"name": "use indigenous and modern knowledge systems for effective decision making in life"},
                        {"name": "appreciate the indigenous knowledge systems in the society"},
                    ],
                    "learning_experiences": [
                        "brainstorm in pairs on various types of indigenous knowledge systems in African societies",
                        "use print or digital resources to research on how indigenous knowledge systems were used",
                        "in pairs, devise ways of using indigenous and modern knowledge systems",
                        "value others' ideas as they debate on how indigenous knowledge systems are applied in various fields"
                    ],
                    "inquiry_questions": ["How does indigenous knowledge influence on the modern society?"],
                    "core_competencies": ["Self-efficacy", "Communication and collaboration"],
                    "values": ["Patriotism", "Respect"],
                    "pcis": ["Social cohesion", "Self-awareness"]
                },
                {
                    "name": "Poverty Reduction",
                    "slos": [
                        {"name": "explain causes of poverty in Africa"},
                        {"name": "examine the effects of overexploitation of natural resources on poverty in Africa"},
                        {"name": "apply creative thinking skills to reduce poverty in the society"},
                        {"name": "recognize the contribution of poverty reduction strategies in society"},
                    ],
                    "learning_experiences": [
                        "brainstorm on the causes of poverty in Africa and present their findings",
                        "discuss on the effects of overexploitation of natural resources on poverty in Africa",
                        "illustrate in pairs problem solving skills to reduce poverty in the community",
                        "watch documentaries/video clips on solutions to poverty reduction",
                        "use print or digital resources to explore home-grown practical solutions to poverty reduction",
                        "compose and sing songs/recite poems on sustainable use of resources",
                        "create posters on sustainable use of resources in the community"
                    ],
                    "inquiry_questions": ["What are the measures taken by African governments to reduce poverty?", "How does prudent utilization of resources help to reduce poverty in the society?"],
                    "core_competencies": ["Digital literacy", "Citizenship"],
                    "values": ["Responsibility", "Social justice"],
                    "pcis": ["Poverty reduction", "Environmental education"]
                },
                {
                    "name": "Population Structure",
                    "slos": [
                        {"name": "identify sources of population data in a country"},
                        {"name": "explain factors determining population structure in Kenya and Germany"},
                        {"name": "construct age-sex population pyramids of developed and developing countries"},
                        {"name": "determine the significance of population structure in distribution of national resources"},
                        {"name": "appreciate the differences in population structure between developed and developing countries"},
                    ],
                    "learning_experiences": [
                        "brainstorm on sources of population data",
                        "engage a resource person to discuss factors determining population structure",
                        "use digital or print resources to identify factors determining population structure",
                        "draw age-sex population pyramid of developed and developing countries",
                        "brainstorm and enumerate the significance of population structure in distribution of resources",
                        "compose and display messages on differences in population structure"
                    ],
                    "inquiry_questions": ["Why is population structure of a country important?"],
                    "core_competencies": ["Creativity and imagination", "Communication and collaboration"],
                    "values": ["Unity", "Respect"],
                    "pcis": ["Citizenship", "Effective Communication"]
                },
                {
                    "name": "Peaceful Conflict Resolution",
                    "slos": [
                        {"name": "explain types of peace for sustainable social interactions"},
                        {"name": "identify barriers to conflict resolution in day-to-day lives"},
                        {"name": "explore ways of managing emotions in promotion of peace in the community"},
                        {"name": "apply emotional intelligence for peaceful conflict resolutions in the community"},
                        {"name": "embrace peace initiatives and agreements at the community level for harmonious living"},
                    ],
                    "learning_experiences": [
                        "brainstorm on types of peace in the society (personal, cultural)",
                        "use digital or print resources to search for barriers to conflict resolution",
                        "discuss possible solutions of managing emotions to promote peace",
                        "engage a resource person on how to apply emotional intelligence to maintain peace",
                        "role play community activities on cultivating peace initiatives",
                        "compose songs or poems on non-violent conflict resolution"
                    ],
                    "inquiry_questions": ["How can we promote peace in the community?"],
                    "core_competencies": ["Creativity and imagination", "Critical Thinking and Problem Solving"],
                    "values": ["Peace", "Integrity"],
                    "pcis": ["Social cohesion", "Self Esteem"]
                },
                {
                    "name": "Healthy relationships",
                    "slos": [
                        {"name": "explain ways of sustaining healthy relationships in the community"},
                        {"name": "explore barriers to harmonious relationships"},
                        {"name": "design strategies to overcome barriers to healthy relationships"},
                        {"name": "appreciate the need for healthy relationships in the community"},
                    ],
                    "learning_experiences": [
                        "brainstorm in pairs ways of sustaining healthy relationships",
                        "speak clearly and effectively as they discuss barriers to harmonious relationships",
                        "watch video clips on barriers to healthy relationships and write a report",
                        "use digital or print resources to research on strategies to overcome barriers",
                        "role play scenarios that depict effective communication, negotiation skills, empathy and assertiveness"
                    ],
                    "inquiry_questions": ["How can we promote healthy relationships in the community?"],
                    "core_competencies": ["Communication and Collaboration", "Creativity and imagination"],
                    "values": ["Peace", "Unity"],
                    "pcis": ["Social cohesion"]
                },
            ]
        },
        {
            "name": "Natural and Historic Built Environments",
            "substrands": [
                {
                    "name": "Topographical maps",
                    "slos": [
                        {"name": "describe human activities on topographical maps"},
                        {"name": "use creative thinking skills to enlarge and reduce parts of topographical maps"},
                        {"name": "illustrate cross-sections from topographical maps"},
                        {"name": "appreciate representation of human activities on topographical maps"},
                    ],
                    "learning_experiences": [
                        "brainstorm human activities that may be represented on a topographical map",
                        "use print or digital resources to find out how human activities are represented",
                        "draw a sketch map to enlarge and reduce part of topographical maps",
                        "draw cross-sections from topographical maps showing human activities",
                        "display the cross-sections",
                        "take a gallery walk and peer assess"
                    ],
                    "inquiry_questions": ["Why are topographical maps important?"],
                    "core_competencies": ["Digital literacy", "Learning to Learn"],
                    "values": ["Integrity", "Love"],
                    "pcis": ["Self Esteem", "Peer education"]
                },
                {
                    "name": "Internal Land Forming Processes",
                    "slos": [
                        {"name": "explore the types and causes of earth movements in the environment"},
                        {"name": "explain the theories of continental drift and plate tectonics in the formation of continents"},
                        {"name": "illustrate the formation of selected features due to faulting in the environment"},
                        {"name": "explain the effects of faulting to human activities"},
                        {"name": "recognise internal land forming processes in shaping the landscape"},
                    ],
                    "learning_experiences": [
                        "brainstorm the types and causes of earth movements",
                        "conduct library research on types of faults in the environment",
                        "use digital or print resources to research on theories of continental drift and plate tectonics",
                        "carry out mapping on the significance of faulting to human life",
                        "Develop posters to create awareness on disasters relating to faulting",
                        "view video clips/documentaries on the processes of faulting",
                        "draw a sketch illustrating the formation of selected features",
                        "use an atlas to locate features formed as a result of faulting process",
                        "brainstorm and share in class the significance of faulting on human activities"
                    ],
                    "inquiry_questions": ["How do landforms influence human activities?"],
                    "core_competencies": ["Digital literacy", "Learning to Learn"],
                    "values": ["Respect", "Responsibility"],
                    "pcis": ["Environmental education", "Disaster risk reduction"]
                },
                {
                    "name": "Multi-purpose River Projects in Africa",
                    "slos": [
                        {"name": "identify selected multi-purpose river projects on a map of Africa"},
                        {"name": "outline the conditions that led to the establishment of multi-purpose river projects along river Tana"},
                        {"name": "examine the economic importance of multi-purpose river projects in Africa"},
                        {"name": "assess challenges facing multi-purpose river projects in Africa"},
                        {"name": "design solutions to challenges facing multi-purpose river projects in Africa"},
                        {"name": "recognise the importance of multipurpose river projects in the society"},
                    ],
                    "learning_experiences": [
                        "use internet and print media to identify selected multi-purpose river projects",
                        "discuss the conditions that led to the establishment of multi-purpose river projects along River Tana",
                        "carry out research on the economic importance of multi-purpose river projects",
                        "brainstorm on challenges facing multi-purpose river projects in Africa",
                        "invite a resource person to share on the solutions to challenges"
                    ],
                    "inquiry_questions": ["How useful are multi-purpose river projects in society?"],
                    "core_competencies": ["Digital literacy", "Communication and collaboration"],
                    "values": ["Responsibility", "Social Justice"],
                    "pcis": ["Creative thinking skills", "Financial literacy"]
                },
                {
                    "name": "Management and Conservation of the Environment",
                    "slos": [
                        {"name": "explore factors that lead to degradation of the environment in the community"},
                        {"name": "describe the effects of environmental degradation in society"},
                        {"name": "design measures to manage and conserve the environment for sustainability"},
                        {"name": "apply creative thinking skills in managing and conserving the immediate environment"},
                        {"name": "acknowledge the importance of managing and conserving the environment"},
                    ],
                    "learning_experiences": [
                        "research on factors that leads to degradation of the environment in the community",
                        "view video clips or documentaries and write an essay on degradation factors",
                        "use print or digital resources to establish effects of degradation of the environment",
                        "brainstorm on the difference between management and conservation of the environment",
                        "demonstrate tolerance and express different viewpoints as they participate in conservation",
                        "develop and display posters with messages on how to manage and conserve the environment"
                    ],
                    "inquiry_questions": ["Why is it important to conserve degraded environment?"],
                    "core_competencies": ["Critical thinking and problem-solving", "Citizenship"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Environmental education", "Social cohesion"]
                },
                {
                    "name": "World Heritage Sites in Africa",
                    "slos": [
                        {"name": "identify the selected world heritage sites in Africa"},
                        {"name": "examine importance of the selected world sites in promoting cultural heritage"},
                        {"name": "design measures to conserve the selected world heritage sites"},
                        {"name": "apply critical thinking skills in conserving heritage sites within the locality"},
                        {"name": "value heritage sites in the community"},
                    ],
                    "learning_experiences": [
                        "use digital/print resources to locate the selected world heritage sites",
                        "brainstorm on the importance of world sites in promoting cultural heritage",
                        "compose and sing songs or recite poems on the importance of world heritage sites",
                        "formulate in pairs measures to conserve heritage sites"
                    ],
                    "inquiry_questions": ["Why is it important to conserve the world heritage sites?"],
                    "core_competencies": ["Creativity and imagination", "Citizenship"],
                    "values": ["Social justice", "Love"],
                    "pcis": ["Social cohesion", "Self-esteem"]
                },
            ]
        },
        {
            "name": "Political Developments and Governance",
            "substrands": [
                {
                    "name": "The Constitution of Kenya",
                    "slos": [
                        {"name": "identify the stages in the constitution-making process in Kenya"},
                        {"name": "examine the role of parliament in constitution-making process"},
                        {"name": "explore the role of citizens in constitution-making process"},
                        {"name": "participate in the constitution-making process in community"},
                        {"name": "desire to defend and promote the Constitution of Kenya"},
                    ],
                    "learning_experiences": [
                        "Carry out research on the stages in constitution-making process in Kenya",
                        "create posters on the stages of the constitution-making process",
                        "watch video clips on parliamentary debate on the constitution-making process",
                        "engage a resource person to talk about the role of citizens",
                        "role play citizens participating in constitution-making process",
                        "role play on the values that should be exercised during constitution making",
                        "sing patriotic songs on defending and promoting the Constitution of Kenya"
                    ],
                    "inquiry_questions": ["Why is constitution-making process in Kenya important?"],
                    "core_competencies": ["Citizenship", "Learning to learn"],
                    "values": ["Patriotism", "Unity"],
                    "pcis": ["Rule of Law", "Good governance"]
                },
                {
                    "name": "Civic Engagement in Governance",
                    "slos": [
                        {"name": "identify individual and collective civic engagement activities in Kenya"},
                        {"name": "illustrate the role of political parties in democratic governance"},
                        {"name": "outline positions vied for in a general election in Kenya"},
                        {"name": "exhibit values that promote ethical civic engagement in the community"},
                    ],
                    "learning_experiences": [
                        "brainstorm on individual and collective civic engagement activities in Kenya",
                        "develop slogans on individual and collective civic engagement",
                        "create posters on personal and civic engagement activities",
                        "discuss the basic constitutional requirements for political parties as stipulated in Article 91",
                        "discuss the role of political parties in democratic governance",
                        "design charts on various elective positions in Kenya",
                        "role play scenarios that bring out values that promote ethical civic engagement"
                    ],
                    "inquiry_questions": ["How does civic engagement promote good governance in the country?", "How can we participate in democratic processes in the society?"],
                    "core_competencies": ["Critical thinking and problem solving", "Self-Efficacy"],
                    "values": ["Respect", "Peace"],
                    "pcis": ["Civic Education", "Assertiveness"]
                },
                {
                    "name": "Kenya's Bill of Rights",
                    "slos": [
                        {"name": "explore Kenya's Bill of Rights for mutual social well-being"},
                        {"name": "examine human rights of special groups for promotion of social justice and inclusivity"},
                        {"name": "apply the bill of rights for harmonious living"},
                        {"name": "develop assertiveness necessary in standing up for human rights"},
                        {"name": "cultivate empathy and solidarity with special groups in society"},
                        {"name": "embrace respect for human rights in society"},
                    ],
                    "learning_experiences": [
                        "use digital or print resources to research on Kenya's bill of right",
                        "debate on human rights of special groups (Elderly, Refugees, Migrants)",
                        "carry out research to gather information on the rights of special groups",
                        "design posters on human rights laws with regard to special groups",
                        "discuss ways in which the bill of rights are applied to foster harmonious living",
                        "role play situations/scenarios that bring out assertiveness in standing up for rights",
                        "brainstorm on human rights laws for protection of special groups",
                        "develop strategies for promoting protection of special groups in the community"
                    ],
                    "inquiry_questions": ["How can we protect the special groups in the community?"],
                    "core_competencies": ["Citizenship", "Creativity and Imagination"],
                    "values": ["Unity", "Patriotism"],
                    "pcis": ["Clubs and societies", "Human Rights"]
                },
                {
                    "name": "Cultural Globalization",
                    "slos": [
                        {"name": "identify cultural elements and practices that have acquired a global recognition and status"},
                        {"name": "examine African cultural practices in promoting a common humanity"},
                        {"name": "explore ways of preserving cultural elements that promotes global citizenship"},
                        {"name": "enumerate factors that promote healthy cultural relationships and global interconnectedness"},
                        {"name": "appreciate values and cultural elements which promote responsible global citizenship"},
                    ],
                    "learning_experiences": [
                        "brainstorm on African cultural practices",
                        "use digital or print media resources to research on cultural elements in Kenya with global status",
                        "discuss in groups African cultural practices in promoting a common humanity",
                        "carry out research on ways of preserving cultural elements",
                        "invite a resource person to discuss on ways of preserving cultural elements",
                        "design charts/posters depicting factors that promote healthy cultural relationships",
                        "debate on the role of international cultural exchange in promoting global citizenship"
                    ],
                    "inquiry_questions": ["How can we preserve aspects of cultural globalization in the community?", "What are the merits of cultural globalisation?"],
                    "core_competencies": ["Digital literacy", "Self-efficacy"],
                    "values": ["Respect", "Patriotism"],
                    "pcis": ["Self-awareness", "Social cohesion"]
                },
            ]
        },
    ]
}


# ============================================================================
# KISWAHILI GRADE 9 - Extracted from Kiswahili-Grade-9.pdf
# ============================================================================
KISWAHILI_GRADE_9 = {
    "name": "Kiswahili",
    "strands": [
        {
            "name": "Kusikiliza na Kuzungumza",
            "substrands": [
                {
                    "name": "Kusikiliza na Kujibu: Mjadala",
                    "slos": [
                        {"name": "kutambua vipengele vya kuzingatia katika kusikiliza mjadala"},
                        {"name": "kutambua vipengele vya kuzingatia katika kuchangia mjadala"},
                        {"name": "kushiriki mjadala kwa kuzingatia vipengele vifaavyo"},
                        {"name": "kuchangamkia kushiriki katika mijadala ya muktadha mbalimbali"},
                    ],
                    "learning_experiences": [
                        "kutambua vipengele vya kuzingatia katika kusikiliza mjadala",
                        "kutambua vipengele vya kuzingatia katika kuchangia mjadala",
                        "kusikiliza au kutazama mjadala kuhusu suala lengwa katika kifaa cha kidijitali",
                        "kueleza vipengele vya kusikiliza na kuchangia mjadala vilivyozingatiwa",
                        "kushiriki mjadala kuhusu suala lengwa akizingatia vipengele vifaavyo"
                    ],
                    "inquiry_questions": ["Je, unazingatia nini wakati wa kusikiliza na kuchangia mjadala?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Ujuzi wa kidijitali", "Ubunifu", "Kujiamini"],
                    "values": ["Heshima", "Upendo", "Uwajibikaji", "Umoja"],
                    "pcis": ["Elimu ya mazingira na tabia nchi", "Elimu ya afya ya kujikinga"]
                },
                {
                    "name": "Kusikiliza kwa Kina: Sauti /b/ na /mb/",
                    "slos": [
                        {"name": "kutamka sauti /b/ na /mb/ ipasavyo ili kuzitofautisha kimatamshi"},
                        {"name": "kutamka vitanzandimi vyenye sauti /b/ na /mb/ ipasavyo"},
                        {"name": "kuunda vitanzandimi vyepesi vyenye sauti /b/ na /mb/"},
                        {"name": "kuchangamkia matamshi bora ya sauti /b/ na /mb/ katika mazungumzo ya kawaida"},
                    ],
                    "learning_experiences": [
                        "kutambua sauti /b/ na /mb/ katika maneno na vifungu",
                        "kusikiliza na kutamka vitanzandimi vyepesi vinavyohusisha matamshi ya sauti /b/ na /mb/",
                        "kubuni vitanzandimi vyepesi vinavyohusisha sauti /b/ na /mb/",
                        "kuwasomea wenzake vitanzandimi alivyobuni ili wamtolee maoni"
                    ],
                    "inquiry_questions": ["Kutamka maneno yenye sauti /b/ na /mb/ ipasavyo kuna umuhimu gani?"],
                    "core_competencies": ["Ujuzi wa kidijitali", "Ubunifu", "Kujiamini", "Hamu ya ujifunzaji"],
                    "values": ["Heshima", "Uwajibikaji", "Umoja"],
                    "pcis": ["Afya ya mtu binafsi"]
                },
                {
                    "name": "Mazungumzo: Malumbano ya Utani",
                    "slos": [
                        {"name": "kutambua sifa za malumbano ya utani"},
                        {"name": "kuandaa malumbano ya utani kuhusu mada fulani"},
                        {"name": "kushiriki malumbano ya utani kwa kuzingatia sifa zake"},
                        {"name": "kuthamini malumbano ya utani kama njia ya kuenzi utamaduni"},
                    ],
                    "learning_experiences": [
                        "kusikiliza au kutazama malumbano ya utani katika kifaa cha kidijitali",
                        "kutambua sifa za malumbano ya utani",
                        "kuandaa malumbano ya utani kuhusu mada fulani akiwa na wenzake",
                        "kushiriki malumbano ya utani akizingatia sifa zake"
                    ],
                    "inquiry_questions": ["Malumbano ya utani yana umuhimu gani katika jamii?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Ubunifu", "Kujiamini"],
                    "values": ["Heshima", "Upendo", "Umoja"],
                    "pcis": ["Elimu ya kiraia"]
                },
            ]
        },
        {
            "name": "Kusoma",
            "substrands": [
                {
                    "name": "Kusoma kwa Ufahamu: Habari",
                    "slos": [
                        {"name": "kutambua aina mbalimbali za habari"},
                        {"name": "kusoma habari kwa sauti na kimya"},
                        {"name": "kujibu maswali kuhusu habari iliyosomwa"},
                        {"name": "kuchangamkia kusoma habari mbalimbali"},
                    ],
                    "learning_experiences": [
                        "kutambua aina mbalimbali za habari",
                        "kusoma habari kwa sauti na kimya",
                        "kujibu maswali kuhusu habari iliyosomwa",
                        "kujadili maudhui ya habari aliyoisoma akiwa na wenzake"
                    ],
                    "inquiry_questions": ["Kusoma habari mbalimbali kuna umuhimu gani?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Ujuzi wa kidijitali", "Kujiamini"],
                    "values": ["Heshima", "Uwajibikaji"],
                    "pcis": ["Elimu ya vyombo vya habari"]
                },
                {
                    "name": "Kusoma kwa Kina: Ushairi",
                    "slos": [
                        {"name": "kutambua vipengele vya ushairi katika shairi"},
                        {"name": "kufasiri shairi kulingana na muktadha wake"},
                        {"name": "kutambua ujumbe katika shairi"},
                        {"name": "kuthamini ushairi kama sanaa ya lugha"},
                    ],
                    "learning_experiences": [
                        "kusoma mashairi mbalimbali kwa sauti na kimya",
                        "kutambua vipengele vya ushairi katika shairi",
                        "kufasiri shairi kulingana na muktadha wake",
                        "kutambua ujumbe katika shairi",
                        "kutunga shairi fupi kuhusu mada fulani"
                    ],
                    "inquiry_questions": ["Ushairi una umuhimu gani katika jamii?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Ubunifu", "Kujiamini"],
                    "values": ["Heshima", "Upendo", "Umoja"],
                    "pcis": ["Elimu ya sanaa"]
                },
            ]
        },
        {
            "name": "Kuandika",
            "substrands": [
                {
                    "name": "Insha za Kubuni",
                    "slos": [
                        {"name": "kutambua sifa za insha za kubuni"},
                        {"name": "kupanga mawazo kuhusu mada ya insha"},
                        {"name": "kuandika insha ya kubuni kulingana na sifa zake"},
                        {"name": "kuchangamkia kuandika insha za kubuni"},
                    ],
                    "learning_experiences": [
                        "kutambua sifa za insha za kubuni",
                        "kupanga mawazo kuhusu mada ya insha",
                        "kuandika insha ya kubuni kulingana na sifa zake",
                        "kusoma insha aliyoandika mbele ya wenzake ili wamtolee maoni"
                    ],
                    "inquiry_questions": ["Insha za kubuni zina umuhimu gani?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Ubunifu", "Kujiamini"],
                    "values": ["Heshima", "Uwajibikaji"],
                    "pcis": ["Elimu ya sanaa"]
                },
                {
                    "name": "Barua ya Kuomba Kazi",
                    "slos": [
                        {"name": "kutambua muundo wa barua ya kuomba kazi"},
                        {"name": "kuandika barua ya kuomba kazi kwa kuzingatia muundo wake"},
                        {"name": "kuthamini barua ya kuomba kazi kama hati muhimu ya maombi ya ajira"},
                    ],
                    "learning_experiences": [
                        "kutambua muundo wa barua ya kuomba kazi",
                        "kuandika barua ya kuomba kazi kwa kuzingatia muundo wake",
                        "kusoma barua aliyoandika mbele ya wenzake ili wamtolee maoni"
                    ],
                    "inquiry_questions": ["Barua ya kuomba kazi ina umuhimu gani?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujiamini"],
                    "values": ["Heshima", "Uwajibikaji"],
                    "pcis": ["Elimu ya ajira"]
                },
            ]
        },
        {
            "name": "Sarufi",
            "substrands": [
                {
                    "name": "Vihusishi",
                    "slos": [
                        {"name": "kutambua vihusishi katika sentensi"},
                        {"name": "kutumia vihusishi ipasavyo katika sentensi"},
                        {"name": "kuchangamkia matumizi sahihi ya vihusishi katika mawasiliano"},
                    ],
                    "learning_experiences": [
                        "kutambua vihusishi katika sentensi",
                        "kutumia vihusishi ipasavyo katika sentensi",
                        "kuunda sentensi kwa kutumia vihusishi mbalimbali"
                    ],
                    "inquiry_questions": ["Vihusishi vina umuhimu gani katika sentensi?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujiamini"],
                    "values": ["Heshima", "Uwajibikaji"],
                    "pcis": []
                },
                {
                    "name": "Nyakati na Hali",
                    "slos": [
                        {"name": "kutambua nyakati na hali mbalimbali za vitenzi"},
                        {"name": "kutumia nyakati na hali za vitenzi ipasavyo katika sentensi"},
                        {"name": "kuchangamkia matumizi sahihi ya nyakati na hali katika mawasiliano"},
                    ],
                    "learning_experiences": [
                        "kutambua nyakati na hali mbalimbali za vitenzi",
                        "kutumia nyakati na hali za vitenzi ipasavyo katika sentensi",
                        "kuunda sentensi kwa kutumia nyakati na hali mbalimbali"
                    ],
                    "inquiry_questions": ["Nyakati na hali zina umuhimu gani katika sentensi?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujiamini"],
                    "values": ["Heshima", "Uwajibikaji"],
                    "pcis": []
                },
                {
                    "name": "Ngeli na Upatanisho wa Kisarufi",
                    "slos": [
                        {"name": "kutambua ngeli mbalimbali za nomino"},
                        {"name": "kupatanisha nomino na vitenzi kulingana na ngeli"},
                        {"name": "kuchangamkia upatanisho sahihi wa kisarufi katika mawasiliano"},
                    ],
                    "learning_experiences": [
                        "kutambua ngeli mbalimbali za nomino",
                        "kupatanisha nomino na vitenzi kulingana na ngeli",
                        "kuunda sentensi zinazozingatia upatanisho wa kisarufi"
                    ],
                    "inquiry_questions": ["Upatanisho wa kisarufi una umuhimu gani?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujiamini"],
                    "values": ["Heshima", "Uwajibikaji"],
                    "pcis": []
                },
            ]
        },
    ]
}


# ============================================================================
# ENGLISH GRADE 9 - Extracted from GRADE.9.ENGLISH.pdf
# ============================================================================
ENGLISH_GRADE_9 = {
    "name": "English",
    "strands": [
        {
            "name": "Listening and Speaking",
            "substrands": [
                {
                    "name": "Polite Language",
                    "slos": [
                        {"name": "outline words and phrases used to express euphemism"},
                        {"name": "use euphemism to show politeness in communication"},
                        {"name": "conduct a debate while adhering to conventions of polite language"},
                        {"name": "acknowledge the importance of politeness in communication"},
                    ],
                    "learning_experiences": [
                        "define the term euphemism",
                        "identify examples of polite words and expressions used in a poem or story",
                        "listen to an audio interview and identify euphemism",
                        "simulate an interview from a text and identify euphemism",
                        "use euphemism in a conversation",
                        "make rules for a debating session in groups",
                        "conduct a debate related to the theme, in small groups",
                        "watch or listen to a recorded clip of a debating session in parliament",
                        "create posters with euphemistic words and phrases",
                        "share the posters through social media or the school notice board"
                    ],
                    "inquiry_questions": ["Why should we use polite language?", "Why is it embarrassing to say some words in public?"],
                    "core_competencies": ["Communication and collaboration", "Citizenship"],
                    "values": ["Respect"],
                    "pcis": ["Social cohesion"]
                },
                {
                    "name": "Oral Literature: Short Forms",
                    "slos": [
                        {"name": "identify the characteristics of riddles, tongue twisters and proverbs"},
                        {"name": "explain the functions of riddles, tongue twisters and proverbs"},
                        {"name": "perform riddles, tongue twisters and proverbs"},
                        {"name": "appreciate the importance of short forms in fostering fluency in communication"},
                    ],
                    "learning_experiences": [
                        "collect riddles, proverbs and tongue twisters from books, the internet, and the community",
                        "play riddling games in small groups",
                        "discuss the functions of proverbs, riddles and tongue twisters",
                        "respond to riddles correctly",
                        "fill in crossword puzzles using riddles and proverbs",
                        "suggest alternative responses to given riddles",
                        "create a collection of riddles, proverbs and tongue twisters and display them"
                    ],
                    "inquiry_questions": ["What is the importance of riddles, proverbs and tongue twisters?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving"],
                    "values": ["Unity"],
                    "pcis": ["Ethnic and racial relationships"]
                },
                {
                    "name": "Listening Comprehension (Grade Appropriate Texts)",
                    "slos": [
                        {"name": "identify the main idea and specific details from an argumentative text"},
                        {"name": "listen for the main idea and specific information (details) in an argumentative text"},
                        {"name": "acknowledge the need for comprehension in communication"},
                    ],
                    "learning_experiences": [
                        "listen to a passage read out by the teacher based on the theme",
                        "pick out specific details such as time, places, events and people from a listening passage",
                        "identify the main idea from a listening text in small groups",
                        "listen to a news bulletin and pick out the main idea and specific details",
                        "watch a debate or interview and pick out required information",
                        "watch a video of a presentation of a poem, song or story and identify specific details",
                        "infer the meaning of unfamiliar words in groups",
                        "answer questions based on the passage"
                    ],
                    "inquiry_questions": ["Why is listening comprehension important?"],
                    "core_competencies": ["Learning to learn", "Digital literacy", "Critical thinking and problem solving"],
                    "values": ["Patriotism", "Responsibility"],
                    "pcis": ["Social cohesion"]
                },
            ]
        },
        {
            "name": "Reading",
            "substrands": [
                {
                    "name": "Independent Reading - Grade Appropriate Text",
                    "slos": [
                        {"name": "select reading materials from digital or non-digital sources"},
                        {"name": "read grade appropriate materials for lifelong learning"},
                        {"name": "create a reading log for monitoring reading activities"},
                        {"name": "recommend to peers suitable fiction and non fiction materials to read"},
                    ],
                    "learning_experiences": [
                        "identify reading materials in a variety of subjects",
                        "search for online fiction and non fiction texts",
                        "skim through a text to obtain the gist (main idea)",
                        "scan a text to obtain specific details",
                        "read the text",
                        "maintain a reading log showing reading activities and thoughts about what they read",
                        "engage in follow up activities such as creating chain stories, forming a book club, keeping vocabulary journals"
                    ],
                    "inquiry_questions": ["Why is independent reading important?"],
                    "core_competencies": ["Learning to learn", "Critical thinking and problem solving", "Self-efficacy"],
                    "values": ["Responsibility"],
                    "pcis": ["Social cohesion"]
                },
                {
                    "name": "Intensive Reading: Simple Poems",
                    "slos": [
                        {"name": "identify basic aspects of style such as repetition and rhyme in a poem"},
                        {"name": "describe the functions of rhyme and repetition in a poem"},
                        {"name": "appreciate the role of repetition and rhyme in a poem"},
                    ],
                    "learning_experiences": [
                        "read provided simple poems individually and in groups",
                        "respond to questions based on a poem",
                        "recite simple poems",
                        "identify the parts of a poem in which repetition and rhyme are used",
                        "search the internet or other sources for more examples of poems",
                        "relate the ideas in a poem to real life",
                        "Compose a simple poem with rhyme and repetition and present in groups"
                    ],
                    "inquiry_questions": ["What is the role of repetition and rhyme in poetry?"],
                    "core_competencies": ["Self-efficacy", "Learning to learn", "Communication and collaboration"],
                    "values": ["Unity", "Respect"],
                    "pcis": ["Effective communication"]
                },
                {
                    "name": "Reading for Information and Meaning",
                    "slos": [
                        {"name": "infer the meaning of words, phrases and sentences from the context"},
                        {"name": "make connections between events in a text and real life situations"},
                        {"name": "value the need to comprehend the information in written texts"},
                    ],
                    "learning_experiences": [
                        "read a grade appropriate text",
                        "make predictions about a reading text",
                        "infer the meaning of new words, phrases and sentences from the context",
                        "look up the meaning of new words and phrases from the dictionary",
                        "relate the characters, events and places in a text to real life",
                        "answer questions from a text",
                        "make notes as they read a text",
                        "summarise the events in a text",
                        "form sentences using the new words and phrases",
                        "fill in a crossword puzzle using the new words"
                    ],
                    "inquiry_questions": ["Why is reading comprehension important?"],
                    "core_competencies": ["Communication"],
                    "values": ["Respect"],
                    "pcis": ["Environmental education"]
                },
            ]
        },
        {
            "name": "Grammar in Use",
            "substrands": [
                {
                    "name": "Gender Neutral Language",
                    "slos": [
                        {"name": "identify gender biased words and phrases in oral and written texts"},
                        {"name": "use gender neutral words and phrases in sentences"},
                        {"name": "acknowledge the importance of gender sensitivity in communication"},
                    ],
                    "learning_experiences": [
                        "listen to common English songs and pick out gender biased words and phrases",
                        "read sections of a poem or story and pick out words with gender bias",
                        "watch a video and identify gender biased and gender neutral terms used by the speakers",
                        "replace the words with gender bias with gender neutral words and phrases",
                        "use the gender neutral words and phrases to make sentences",
                        "rewrite/paraphrase short texts to eliminate gender bias",
                        "collaborate with peers to create posters showing gender neutral words and phrases",
                        "fill in a crossword puzzle featuring gender neutral words/phrases"
                    ],
                    "inquiry_questions": ["Why is gender neutral language important?"],
                    "core_competencies": ["Self-efficacy", "Critical thinking and problem solving"],
                    "values": ["Unity", "Respect"],
                    "pcis": ["Social cohesion"]
                },
                {
                    "name": "Nouns and Quantifiers",
                    "slos": [
                        {"name": "use quantifiers in sentence"},
                        {"name": "categorise count and non-count nouns in oral and written texts"},
                        {"name": "acknowledge the importance of quantifiers in oral and written communication"},
                    ],
                    "learning_experiences": [
                        "read a short passage in which quantifiers are used to describe count and non-count nouns",
                        "listen to a text that uses quantifiers with count and non-count nouns",
                        "identify quantifiers that are used with count, non-count or both categories",
                        "work in small groups to identify count, non-count nouns and quantifiers from a passage",
                        "match count and non-count nouns with the correct quantifiers",
                        "search for more examples of quantifiers from books, newspapers, magazines, and the internet",
                        "form sentences using different quantifiers with count and non-count nouns"
                    ],
                    "inquiry_questions": ["Why are quantifiers important in communication?"],
                    "core_competencies": ["Learning to learn"],
                    "values": ["Unity", "Responsibility"],
                    "pcis": ["Effective communication"]
                },
                {
                    "name": "Modal Auxiliaries",
                    "slos": [
                        {"name": "identify modal auxiliaries in a passage"},
                        {"name": "use modal auxiliaries to express different moods"},
                        {"name": "value the importance of using modal auxiliaries in communication"},
                    ],
                    "learning_experiences": [
                        "identify the modal auxiliaries – may, might, will, shall, would, should, can and could – in a print or digital text",
                        "form sentences using the modal auxiliaries",
                        "read a dialogue featuring modal auxiliaries in pairs",
                        "create a dialogue featuring modal auxiliaries in pairs, record the dialogue and share it with peers",
                        "listen to a song or read a poem and identify the modal auxiliaries used",
                        "view pictures and diagrams and ask questions using modal auxiliaries",
                        "use modal auxiliaries correctly to express permission, requests, ability and obligation",
                        "in groups, discuss the functions of modal auxiliaries"
                    ],
                    "inquiry_questions": ["What are the functions of modal auxiliaries?"],
                    "core_competencies": ["Self efficacy"],
                    "values": ["Respect"],
                    "pcis": ["Effective communication"]
                },
            ]
        },
        {
            "name": "Writing",
            "substrands": [
                {
                    "name": "Legibility and Neatness",
                    "slos": [
                        {"name": "identify sections of a piece of writing that require breaking of words and indentation"},
                        {"name": "indent paragraphs when writing a composition"},
                        {"name": "create a neat and legible text"},
                        {"name": "appreciate the importance of legibility and neatness in written communication"},
                    ],
                    "learning_experiences": [
                        "distinguish between tidy and untidy pieces of writing",
                        "indent paragraphs appropriately",
                        "find out the advantages of a neat and legible handwriting from the internet or non-digital sources",
                        "break words correctly at the end of a line",
                        "assess their own handwriting",
                        "work jointly to review a text written by a peer",
                        "take notes during an oral presentation",
                        "take notes while listening to an audio or watching a video recording",
                        "rewrite portions of a dictated text",
                        "work in partnership with peers to discuss techniques of improving legibility in writing"
                    ],
                    "inquiry_questions": ["Why is neat and legible handwriting important?"],
                    "core_competencies": ["Digital literacy", "Learning to learn"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Effective communication"]
                },
                {
                    "name": "Mechanics of Writing: Punctuation",
                    "slos": [
                        {"name": "identify the double quotation marks and the bracket in a text"},
                        {"name": "use the double quotation marks and the bracket in written texts"},
                        {"name": "appreciate the role of the double quotation marks and the bracket in written texts"},
                    ],
                    "learning_experiences": [
                        "identify the double quotation marks and the bracket in digital texts, newspapers, books or magazines",
                        "make sentences using the double quotation marks and the bracket",
                        "assess the work of peers",
                        "make posters displaying the correct use of the double quotation marks and the bracket"
                    ],
                    "inquiry_questions": ["Why are punctuation marks important in writing?"],
                    "core_competencies": ["Self-efficacy", "Creativity and imagination", "Learning to learn"],
                    "values": ["Love", "Unity"],
                    "pcis": ["Effective communication", "Creative thinking"]
                },
                {
                    "name": "Structure of a paragraph",
                    "slos": [
                        {"name": "outline the four characteristics of a well formed paragraph"},
                        {"name": "create a paragraph that is well developed, coherent and unified"},
                        {"name": "acknowledge the need for concise paragraphs in written communication"},
                    ],
                    "learning_experiences": [
                        "read excerpts from newspaper articles, magazines, textbooks or online articles",
                        "identify the topic sentence, supporting sentences, and clincher sentence",
                        "discuss the steps for paragraph writing",
                        "write a paragraph on a topic of interest that is coherent, unified, and well-developed",
                        "assess the paragraphs in groups"
                    ],
                    "inquiry_questions": ["What makes a good paragraph?"],
                    "core_competencies": ["Digital literacy"],
                    "values": ["Unity"],
                    "pcis": ["Effective communication"]
                },
            ]
        },
        {
            "name": "Intensive Reading: Play",
            "substrands": [
                {
                    "name": "Play: Structure and Setting",
                    "slos": [
                        {"name": "describe the structure and setting of a play"},
                        {"name": "analyse the acts and scenes of a play for literary appreciation"},
                        {"name": "recognise the role of literary appreciation in critical thinking"},
                    ],
                    "learning_experiences": [
                        "outline the order of events in a play",
                        "analyse the acts and scenes in a play",
                        "discuss the action in a play in groups",
                        "describe the time the actions in a play occur",
                        "work jointly with peers to discuss where the events in a play take place",
                        "write a summary of a scene in a play",
                        "collaborate with peers to role play some of the actions and characters in a play",
                        "paraphrase sections of a play"
                    ],
                    "inquiry_questions": ["What is the importance of structure and setting in a play?"],
                    "core_competencies": ["Self efficacy", "Communication and collaboration", "Creativity and imagination"],
                    "values": ["Unity", "Responsibility"],
                    "pcis": ["Nationalism"]
                },
                {
                    "name": "Intensive Reading: Plot",
                    "slos": [
                        {"name": "describe the sequence of events in a play"},
                        {"name": "relate the events in a play to real life experiences"},
                        {"name": "acknowledge the importance of a plot in a literary work"},
                    ],
                    "learning_experiences": [
                        "read a play individually and in small groups",
                        "identify the key events in a play",
                        "role-play a section of a play in groups",
                        "analyse the events in a play",
                        "answer questions based on the plot",
                        "create a summary of the key events",
                        "assess the summary in pairs or small groups",
                        "make connections between events in a play and real life"
                    ],
                    "inquiry_questions": ["Why is plot important in a literary work?"],
                    "core_competencies": ["Learning to learn", "Communication and collaboration"],
                    "values": ["Unity"],
                    "pcis": ["Social cohesion"]
                },
                {
                    "name": "Play: Identification of Characters",
                    "slos": [
                        {"name": "identify the characters in a play"},
                        {"name": "use appropriate adjectives to describe the characters"},
                        {"name": "describe the actions of the characters using appropriate adverbs"},
                        {"name": "value the need to describe people and situations appropriately"},
                    ],
                    "learning_experiences": [
                        "list the characters and their roles in a play",
                        "use appropriate adjectives to describe the characters",
                        "describe actions of characters using appropriate adverbs",
                        "discuss in groups the traits of selected characters",
                        "role play selected characters"
                    ],
                    "inquiry_questions": ["Why is characterisation important in a play?"],
                    "core_competencies": ["Communication and collaboration", "Creativity and imagination"],
                    "values": ["Respect"],
                    "pcis": ["Social cohesion"]
                },
            ]
        },
    ]
}


# All subjects to seed for Grade 9
ALL_GRADE_9_SUBJECTS = [
    MATHEMATICS_GRADE_9,
    INTEGRATED_SCIENCE_GRADE_9,
    SOCIAL_STUDIES_GRADE_9,
    KISWAHILI_GRADE_9,
    ENGLISH_GRADE_9,
]


async def find_or_create_grade(grade_name: str):
    """Find or create a grade."""
    grade = await db.grades.find_one({"name": grade_name})
    if not grade:
        result = await db.grades.insert_one({"name": grade_name})
        return result.inserted_id
    return grade["_id"]


async def find_subject_by_name(subject_name: str):
    """Find a subject by name."""
    return await db.subjects.find_one({"name": subject_name})


async def ensure_subject_has_grade(subject_id: ObjectId, grade_id: ObjectId):
    """Ensure a subject has a grade in its gradeIds array."""
    grade_id_str = str(grade_id)
    subject = await db.subjects.find_one({"_id": subject_id})
    if subject:
        current_grade_ids = subject.get("gradeIds", [])
        # Check if grade_id already exists (as string or ObjectId)
        if grade_id_str not in current_grade_ids and grade_id not in current_grade_ids:
            current_grade_ids.append(grade_id_str)
            await db.subjects.update_one(
                {"_id": subject_id},
                {"$set": {"gradeIds": current_grade_ids}}
            )
            print(f"  Added Grade 9 to subject {subject['name']}")


async def delete_existing_grade9_data(subject_id: ObjectId):
    """Delete existing strands, substrands, slos, and learning_activities for a subject."""
    # Get all strands for this subject
    strands = await db.strands.find({"subjectId": subject_id}).to_list(length=1000)
    
    for strand in strands:
        strand_id = strand["_id"]
        
        # Get all substrands for this strand
        substrands = await db.substrands.find({"strandId": strand_id}).to_list(length=1000)
        
        for substrand in substrands:
            substrand_id = substrand["_id"]
            
            # Get all SLOs for this substrand
            slos = await db.slos.find({"substrandId": substrand_id}).to_list(length=1000)
            
            for slo in slos:
                # Delete learning activities for this SLO
                await db.learning_activities.delete_many({"sloId": slo["_id"]})
            
            # Delete SLOs for this substrand
            await db.slos.delete_many({"substrandId": substrand_id})
        
        # Delete substrands for this strand
        await db.substrands.delete_many({"strandId": strand_id})
    
    # Delete strands for this subject
    await db.strands.delete_many({"subjectId": subject_id})


async def seed_subject(subject_data: dict, grade_id: ObjectId):
    """Seed curriculum data for a single subject."""
    subject_name = subject_data["name"]
    print(f"\n{'='*60}")
    print(f"Processing: {subject_name}")
    print(f"{'='*60}")
    
    # Find existing subject
    subject = await find_subject_by_name(subject_name)
    
    if not subject:
        print(f"  WARNING: Subject '{subject_name}' not found in database. Skipping.")
        return
    
    subject_id = subject["_id"]
    print(f"  Found subject ID: {subject_id}")
    
    # Ensure subject has Grade 9
    await ensure_subject_has_grade(subject_id, grade_id)
    
    # Delete existing Grade 9 data for this subject
    print(f"  Deleting existing curriculum data for {subject_name}...")
    await delete_existing_grade9_data(subject_id)
    
    strand_count = 0
    substrand_count = 0
    slo_count = 0
    activity_count = 0
    
    # Create strands
    for strand_data in subject_data["strands"]:
        strand_result = await db.strands.insert_one({
            "name": strand_data["name"],
            "subjectId": subject_id,
            "createdAt": datetime.utcnow()
        })
        strand_id = strand_result.inserted_id
        strand_count += 1
        print(f"  Created Strand: {strand_data['name']}")
        
        # Create substrands
        for substrand_data in strand_data["substrands"]:
            substrand_result = await db.substrands.insert_one({
                "name": substrand_data["name"],
                "strandId": strand_id,
                "createdAt": datetime.utcnow()
            })
            substrand_id = substrand_result.inserted_id
            substrand_count += 1
            
            # Create SLOs
            for slo_data in substrand_data["slos"]:
                slo_result = await db.slos.insert_one({
                    "name": slo_data["name"],
                    "description": slo_data.get("description", ""),
                    "substrandId": substrand_id,
                    "createdAt": datetime.utcnow()
                })
                slo_id = slo_result.inserted_id
                slo_count += 1
                
                # Create learning activity for this SLO
                await db.learning_activities.insert_one({
                    "sloId": slo_id,
                    "introduction": ", ".join(substrand_data.get("learning_experiences", [])[:3]),
                    "development": ", ".join(substrand_data.get("learning_experiences", [])[3:6]) if len(substrand_data.get("learning_experiences", [])) > 3 else "",
                    "conclusion": ", ".join(substrand_data.get("learning_experiences", [])[6:]) if len(substrand_data.get("learning_experiences", [])) > 6 else "",
                    "inquiry_questions": substrand_data.get("inquiry_questions", []),
                    "core_competencies": substrand_data.get("core_competencies", []),
                    "pci": substrand_data.get("pcis", []),
                    "values": substrand_data.get("values", []),
                    "createdAt": datetime.utcnow()
                })
                activity_count += 1
    
    print(f"\n  Summary for {subject_name}:")
    print(f"    - Strands: {strand_count}")
    print(f"    - Substrands: {substrand_count}")
    print(f"    - SLOs: {slo_count}")
    print(f"    - Learning Activities: {activity_count}")


async def main():
    """Main function to seed all Grade 9 curriculum data."""
    print("\n" + "="*70)
    print("GRADE 9 ACCURATE CURRICULUM SEEDING")
    print("Data extracted directly from KICD PDFs")
    print("="*70)
    
    # Get or create Grade 9
    grade_id = await find_or_create_grade("Grade 9")
    print(f"\nGrade 9 ID: {grade_id}")
    
    # Seed each subject
    for subject_data in ALL_GRADE_9_SUBJECTS:
        await seed_subject(subject_data, grade_id)
    
    print("\n" + "="*70)
    print("SEEDING COMPLETE!")
    print("="*70)
    
    # Verification
    print("\n--- VERIFICATION ---")
    grade9_id_str = str(grade_id)
    
    for subject_data in ALL_GRADE_9_SUBJECTS:
        subject = await db.subjects.find_one({"name": subject_data["name"]})
        if subject:
            strand_count = await db.strands.count_documents({"subjectId": subject["_id"]})
            print(f"{subject_data['name']}: {strand_count} strands")


if __name__ == "__main__":
    asyncio.run(main())
