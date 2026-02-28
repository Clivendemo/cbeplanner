#!/usr/bin/env python3
"""
Seed specific learning activities for lesson plan generation.
This script adds detailed activities for Introduction, Lesson Development, 
Conclusion, and Extended Activities for each substrand.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Activities data structure - organized by subject -> strand -> substrand
ACTIVITIES_DATA = {
    "Agriculture": {
        "Crop Production": {
            "Agricultural Land": {
                "introduction": [
                    "Teacher introduces the concept of agricultural land by asking learners what they know about farming in their community.",
                    "Brainstorm session on different ways people access land for farming (buying, leasing, inheriting, donation).",
                    "Show pictures/video clips of different types of agricultural land and their uses."
                ],
                "development": [
                    "Discuss with resource persons ways of accessing land for agricultural use including leasing, inheriting, buying, and donation.",
                    "Take an excursion in the community to study and assess different forms of land and discuss possible utilities.",
                    "Use digital devices to search for information on natural factors that determine land productivity (climate, altitude, soil factors, topography, biotic factors).",
                    "Learners work in groups to analyze land samples and determine their suitability for different crops."
                ],
                "conclusion": [
                    "Make class presentations on the importance of land in agricultural production.",
                    "Summarize key factors that determine land productivity.",
                    "Reflection: What new things did you learn about agricultural land today?"
                ],
                "extended": [
                    "Project: Survey land in your community and create a report on its agricultural potential.",
                    "Research online about modern land management practices.",
                    "Interview a local farmer about how they acquired their land and challenges faced."
                ],
                "resources": ["Video clips on land productivity", "Manila papers", "Marker pens", "Digital devices"],
                "assessment": ["Written test", "Written assignment", "Observation of learning activities"]
            },
            "Properties of Soil": {
                "introduction": [
                    "Teacher displays different soil samples and asks learners to describe what they observe.",
                    "Discuss prior knowledge about soil - What do you know about the soil in your area?",
                    "Show photographs of different soil textural classes."
                ],
                "development": [
                    "Discuss physical, chemical, and biological properties of soil for crop production.",
                    "Conduct experiments to test physical properties (porosity, texture), chemical properties (soil pH), and biological properties (humus).",
                    "Take a field excursion, observe, and relate soil profile to crop farming activities.",
                    "Use digital and non-digital resources to search for the importance of soil properties in crop production."
                ],
                "conclusion": [
                    "Present findings from soil experiments to the class.",
                    "Discuss how soil properties affect crop selection in your area.",
                    "Create a soil property chart showing ideal conditions for different crops."
                ],
                "extended": [
                    "Collect soil samples from different locations and compare their properties.",
                    "Design an experiment to improve soil quality using locally available materials.",
                    "Research about soil conservation methods used in your community."
                ],
                "resources": ["Soil samples", "Soil testing kit", "pH indicators", "Sampling tools (jembe, auger, panga)", "Soil containers"],
                "assessment": ["Written assignments", "Observation of learning activities", "Practical experiment reports"]
            },
            "Land Preparation": {
                "introduction": [
                    "Teacher asks: What activities do farmers do before planting crops?",
                    "Brainstorm on the activities carried out on fallow land to prepare an appropriate seedbed.",
                    "Show images/videos of land clearing, primary cultivation, secondary cultivation, and tertiary operations."
                ],
                "development": [
                    "Carry out applicable activities on fallow land to prepare it for crop establishment.",
                    "Demonstrate proper use of farm tools (jembe, fork jembe, panga, slasher) for land preparation.",
                    "Assess the status of land for production and apply conservation tillage practices (zero tillage, minimum tillage).",
                    "Practice different land preparation techniques in the school farm."
                ],
                "conclusion": [
                    "Make presentations on the importance of proper land preparation in crop production.",
                    "Compare different land preparation methods and their advantages.",
                    "Discuss how improper land preparation can affect crop yield."
                ],
                "extended": [
                    "Prepare a plot of land in the school farm using appropriate techniques.",
                    "Research modern land preparation equipment and their benefits.",
                    "Document the land preparation process with photographs for a portfolio."
                ],
                "resources": ["School farm", "Farm tools (jembe, fork jembe, panga, slasher)"],
                "assessment": ["Observation of learning activities", "Written test", "Oral assessment"]
            },
            "Crop Protection": {
                "introduction": [
                    "Teacher shows samples of common weeds and asks learners to identify any they recognize.",
                    "Discuss: Why are weeds a problem for farmers?",
                    "Display photographs of weeds and weed-infested crop fields."
                ],
                "development": [
                    "Take an excursion to identify weeds in a crop field and make a herbarium.",
                    "Use digital and non-digital resources to classify weeds based on morphology and life cycle.",
                    "Discuss in groups the methods of weed control (physical, cultural, biological, chemical, legislative).",
                    "Carry out weed control in a crop field using appropriate methods."
                ],
                "conclusion": [
                    "Discuss and make class presentations on the pros and cons of weeds to a farming household.",
                    "Summarize the most effective weed control methods for different situations.",
                    "Reflect on the economic importance of weeds."
                ],
                "extended": [
                    "Create a weed herbarium with at least 10 different weed species.",
                    "Research integrated weed management approaches.",
                    "Interview farmers about their weed control challenges and solutions."
                ],
                "resources": ["Weed photographs", "Weed herbarium materials", "Herbicides samples", "Knapsack/hand sprayer", "Protective gear"],
                "assessment": ["Observation of weed control activities", "Project portfolio on weed identification", "Oral assessment"]
            }
        },
        "Animal Production": {
            "Breeds of Livestock": {
                "introduction": [
                    "Teacher displays pictures of different livestock breeds and asks learners to name them.",
                    "Discuss: What livestock are commonly reared in your community and why?",
                    "Show video clips of different breeds of cattle, pigs, sheep, goats, and rabbits."
                ],
                "development": [
                    "Use information from digital and print resources to describe breeds of cattle, pigs, rabbits, sheep, and goats.",
                    "Take a field trip or observe resource media to distinguish common breeds based on observable characteristics.",
                    "Create comparison charts showing characteristics and productivity of various breeds.",
                    "Discuss factors to consider when selecting a breed for specific purposes."
                ],
                "conclusion": [
                    "Make presentations on comparative productivity from various livestock breeds.",
                    "Summarize the key distinguishing features of different breed categories.",
                    "Discuss which breeds are most suitable for your local area and why."
                ],
                "extended": [
                    "Visit a livestock farm to observe different breeds in person.",
                    "Research emerging livestock breeds being introduced in Kenya.",
                    "Create a breed identification guide with illustrations."
                ],
                "resources": ["Pictures/videos of livestock breeds", "Live animals (where possible)", "Breed identification charts"],
                "assessment": ["Written test", "Oral assessment while observing breeds", "Breed identification practical"]
            },
            "Animal Handling and Safety": {
                "introduction": [
                    "Teacher asks: What safety measures do you observe around animals?",
                    "Discuss cases of injuries from improper animal handling.",
                    "Show video clips on proper animal handling techniques."
                ],
                "development": [
                    "Discuss inhumane treatments (beating, poor restraining, inappropriate castration, poor transport).",
                    "Use digital devices to observe structures used for safe animal handling.",
                    "Practice using animal handling tools (halter, restraining rope, bull ring, lead stick).",
                    "Demonstrate proper techniques for handling different types of animals."
                ],
                "conclusion": [
                    "Present suggestions on how animal safety could be enhanced in the community.",
                    "Summarize key safety precautions when handling different animals.",
                    "Discuss animal welfare ethics and their importance."
                ],
                "extended": [
                    "Visit nearby farms to observe animal handling practices.",
                    "Design an improved animal handling facility for a specific animal.",
                    "Create a safety poster for animal handling."
                ],
                "resources": ["Animal handling equipment (bull ring, rope, halter)", "Video clips on animal handling", "Safety gear"],
                "assessment": ["Observation of animal handling activities", "Written assignment", "Safety protocol demonstration"]
            },
            "Bee Keeping": {
                "introduction": [
                    "Teacher displays beekeeping equipment and asks learners what they know about bees.",
                    "Discuss the importance of bees in agriculture and the environment.",
                    "Show video on bee behavior and honey production."
                ],
                "development": [
                    "Discuss factors to consider in siting an apiary (water source, forage, security).",
                    "Use digital devices to acquire information on how to stock a hive.",
                    "Deliberate with a resource person on safe apiary management practices.",
                    "Use an empty hive or model to demonstrate honey harvesting process."
                ],
                "conclusion": [
                    "Summarize key considerations for successful beekeeping.",
                    "Discuss the economic potential of beekeeping in your area.",
                    "Reflect on safety measures specific to bee handling."
                ],
                "extended": [
                    "Design an ideal apiary layout for your school.",
                    "Research different types of hives and their advantages.",
                    "Interview a local beekeeper about their practices and challenges."
                ],
                "resources": ["Hives or hive models", "Bee suit", "Smoker", "Hive tool", "Protective equipment"],
                "assessment": ["Written tests", "Observation", "Oral assessment on bee handling safety"]
            }
        },
        "Agricultural Technologies and Entrepreneurship": {
            "Tools and Equipment": {
                "introduction": [
                    "Teacher displays various agricultural tools and asks learners to name and describe their uses.",
                    "Discuss: What tools have you used in farming activities?",
                    "Show video on proper tool use and maintenance."
                ],
                "development": [
                    "Observe and analyze tools used for gardening, livestock production, and assembly tasks.",
                    "Practice using appropriate tools for various agricultural tasks.",
                    "Carry out maintenance practices (cleaning, sharpening, lubrication, repairs).",
                    "Practice safety measures in tool use (proper storage, correct usage, safe distance, PPE)."
                ],
                "conclusion": [
                    "Make presentations on the importance of maintaining tools and equipment.",
                    "Demonstrate proper tool care procedures.",
                    "Discuss the cost implications of poor tool maintenance."
                ],
                "extended": [
                    "Create a tool maintenance schedule for school farm equipment.",
                    "Research innovative agricultural tools used in modern farming.",
                    "Design an improved tool storage system."
                ],
                "resources": ["Agricultural tools (panga, jembe, pruning knife, burdizzo)", "Maintenance materials (oil, sharpening stones)"],
                "assessment": ["Observation of tool use", "Oral assessment", "Practical maintenance demonstration"]
            },
            "Product Processing and Value Addition": {
                "introduction": [
                    "Teacher displays processed agricultural products and asks about their raw materials.",
                    "Discuss: How can we increase the value of farm produce?",
                    "Show examples of value-added products (jam, butter, flour)."
                ],
                "development": [
                    "Use digital resources to search for value addition methods for agricultural produce.",
                    "Discuss with a resource person methods for processing plant products (vegetables, fruits, cereals into jam, juice, flour).",
                    "Practice processing produce of animal origin (milk, honey, meat).",
                    "Learn home-based packaging and branding of processed products."
                ],
                "conclusion": [
                    "Present ethical concerns in processing and value addition.",
                    "Discuss market opportunities for value-added products.",
                    "Calculate potential profits from value addition."
                ],
                "extended": [
                    "Process a selected agricultural product and package it for sale.",
                    "Design branding and labels for a processed product.",
                    "Visit a local processing facility to learn commercial techniques."
                ],
                "resources": ["Heat source", "Cutting tools", "Raw produce (fruits, vegetables, milk, honey)", "Packaging materials"],
                "assessment": ["Observation of processing activities", "Project report", "Product quality assessment"]
            }
        }
    },
    "Biology": {
        "Cell Biology and Biodiversity": {
            "Introduction to Biology": {
                "introduction": [
                    "Teacher asks: Where do you see Biology in your daily life?",
                    "Brainstorm on how biological knowledge affects our lives.",
                    "Show images of various career fields related to Biology."
                ],
                "development": [
                    "Search for information on the meaning and application of Biology in everyday life.",
                    "Collaboratively search from print and non-print media on fields of study (Botany, Zoology, Anatomy, Genetics, etc.).",
                    "Discuss factors influencing career choices (interest, ability) and those that should not (gender, culture, disability).",
                    "Design a career wheel relating Biology fields to careers."
                ],
                "conclusion": [
                    "Present career wheels to the class.",
                    "Discuss the most interesting Biology careers discovered.",
                    "Reflect on how Biology knowledge can improve your community."
                ],
                "extended": [
                    "Interact with resource persons whose careers are related to Biology.",
                    "Research about emerging careers in biotechnology and genetics.",
                    "Create a presentation on your dream Biology-related career."
                ],
                "resources": ["Print and non-print media", "Flash cards", "Career wheel materials", "Resource persons"],
                "assessment": ["Career wheel presentation", "Group discussions", "Written reflections"]
            },
            "Specimen Collection and Preservation": {
                "introduction": [
                    "Teacher displays preserved specimens and collection apparatus.",
                    "Discuss: Why is it important to collect and preserve biological specimens?",
                    "Show examples of a herbarium and preserved animal specimens."
                ],
                "development": [
                    "Search for information on apparatus for collecting specimens (pooter, pitfall trap, sweep net, forceps).",
                    "Improvise apparatus from locally available materials.",
                    "Make a herbarium (pressing, drying, mounting, labeling, storage).",
                    "Collect small animals using appropriate apparatus and preserve them."
                ],
                "conclusion": [
                    "Present preserved specimens to the class.",
                    "Discuss challenges faced during collection and preservation.",
                    "Summarize best practices for specimen preservation."
                ],
                "extended": [
                    "Carry out a project on collecting and preserving specimens from your local environment.",
                    "Create a portfolio documenting your collection process.",
                    "Research about museum preservation techniques."
                ],
                "resources": ["Collection apparatus (pooter, nets, forceps)", "Preservation materials", "Labels", "Herbarium materials"],
                "assessment": ["Project portfolio", "Specimen quality assessment", "Presentation"]
            },
            "Cell Structure and Specialization": {
                "introduction": [
                    "Teacher shows microscope images of cells and asks learners to describe what they see.",
                    "Discuss: What is the basic unit of life?",
                    "Compare everyday magnification (magnifying glass) to microscope magnification."
                ],
                "development": [
                    "Search for information on differences between light and electron microscopes.",
                    "Carry out experiments on preparation of specimen slides (sectioning, staining, mounting, fixation).",
                    "Prepare temporary slides and estimate cell sizes using onion bulbs or kales.",
                    "Use photomicrographs to compare plant and animal cells as seen under electron microscope."
                ],
                "conclusion": [
                    "Draw and label plant and animal cell structures.",
                    "Discuss how specialized cells are adapted to their functions.",
                    "Model the structure of plant and animal cells."
                ],
                "extended": [
                    "Create 3D models of plant and animal cells.",
                    "Research about diseases caused by cell malfunctions.",
                    "Observe permanent slides of specialized cells and create labeled drawings."
                ],
                "resources": ["Light microscope", "Specimen slides", "Staining materials", "Photomicrographs", "Modeling materials"],
                "assessment": ["Slide preparation practical", "Cell drawings", "Model evaluation"]
            },
            "Chemicals of Life": {
                "introduction": [
                    "Teacher displays various food items and asks about their nutritional content.",
                    "Discuss: What chemicals make up living things?",
                    "Show molecular structure diagrams of basic biomolecules."
                ],
                "development": [
                    "Search for information on composition and functions of carbohydrates, proteins, lipids, enzymes, vitamins.",
                    "Carry out experiments to test for carbohydrates, lipids, proteins, and vitamin C in food substances.",
                    "Investigate the presence of catalase enzymes in living tissues.",
                    "Determine factors affecting enzymatic activities (pH, temperature, concentration)."
                ],
                "conclusion": [
                    "Present experiment findings on food tests.",
                    "Examine packaging labels of common food products for nutritional information.",
                    "Discuss the importance of balanced nutrition."
                ],
                "extended": [
                    "Test various local foods for their nutrient content.",
                    "Research about enzyme applications in industry.",
                    "Create a nutrition guide based on your findings."
                ],
                "resources": ["Food samples", "Testing reagents", "Living tissues for enzyme tests", "Food packaging labels"],
                "assessment": ["Experiment reports", "Food test practical", "Packaging label analysis"]
            }
        },
        "Anatomy and Physiology of Plants": {
            "Plant Nutrition": {
                "introduction": [
                    "Teacher shows a healthy green plant and asks: How does this plant make its food?",
                    "Discuss prior knowledge about photosynthesis.",
                    "Show animation of the photosynthesis process."
                ],
                "development": [
                    "Search for information on different types of nutrition in plants.",
                    "Discuss the structure of chloroplast in relation to its function.",
                    "Watch animations on the process of photosynthesis.",
                    "Use illustrations to show reactions during light and dark stages of photosynthesis."
                ],
                "conclusion": [
                    "Present flow charts showing photosynthesis stages.",
                    "Discuss the significance of photosynthesis in nature.",
                    "Relate photosynthesis to food chains and ecosystems."
                ],
                "extended": [
                    "Carry out experiments to demonstrate photosynthesis requirements.",
                    "Research about factors affecting the rate of photosynthesis.",
                    "Create models showing chloroplast structure."
                ],
                "resources": ["Animations/video clips on photosynthesis", "Flow charts", "Plant specimens", "Light sources"],
                "assessment": ["Diagram interpretation", "Group presentations", "Written tests"]
            },
            "Plant Transport": {
                "introduction": [
                    "Teacher shows a wilted plant and a healthy plant, asking learners to explain the difference.",
                    "Discuss: How do plants transport water from roots to leaves?",
                    "Display cross-sections of plant stems."
                ],
                "development": [
                    "Discuss structures of external plant parts in relation to functions.",
                    "Use microscope to observe cross-sections of monocot and dicot roots and stems.",
                    "Carry out experiments to demonstrate water uptake using dye/ink.",
                    "Demonstrate factors affecting the rate of transpiration."
                ],
                "conclusion": [
                    "Present findings from transpiration experiments.",
                    "Compare transport in monocots and dicots.",
                    "Discuss the importance of transport for plant survival."
                ],
                "extended": [
                    "Carry out bark ringing experiment to demonstrate translocation.",
                    "Research about adaptations of plants in water-scarce environments.",
                    "Create labeled diagrams of vascular tissue arrangement."
                ],
                "resources": ["Microscope", "Plant sections", "Dye/ink", "Transparent bags", "Digital devices for animations"],
                "assessment": ["Practical experiments", "Drawings of vascular tissues", "Report writing"]
            },
            "Plant Gaseous Exchange and Respiration": {
                "introduction": [
                    "Teacher asks: Do plants breathe like animals?",
                    "Discuss the difference between photosynthesis and respiration.",
                    "Show images of stomata and lenticels."
                ],
                "development": [
                    "Collect fresh leaves and observe sites of gaseous exchange (stomata, lenticels).",
                    "Search for information on the mechanism of stomatal opening and closing.",
                    "Compare number, size, and distribution of stomata on leaves from different habitats.",
                    "Carry out experiments to distinguish aerobic and anaerobic respiration."
                ],
                "conclusion": [
                    "Discuss the economic importance of anaerobic respiration.",
                    "Present findings on stomata distribution.",
                    "Summarize the significance of gaseous exchange in plants."
                ],
                "extended": [
                    "Carry out a fermentation project (biogas, porridge, silage, baking).",
                    "Research about adaptations of aquatic plants for gaseous exchange.",
                    "Investigate respiration rates under different conditions."
                ],
                "resources": ["Fresh plant specimens", "Photomicrographs", "Digital devices", "Fermentation materials"],
                "assessment": ["Stomata observation practical", "Respiration experiments", "Project on fermentation"]
            }
        },
        "Anatomy and Physiology of Animals": {
            "Animal Nutrition": {
                "introduction": [
                    "Teacher shows images of different insects and birds feeding.",
                    "Discuss: How are animal mouthparts adapted for different types of food?",
                    "Display specimens or models of insect mouthparts."
                ],
                "development": [
                    "Collect specimens of locusts/grasshoppers and observe mouthparts using hand lens.",
                    "Search for information on mouthparts of different insects (biting, piercing, sucking, siphoning).",
                    "Observe images of bird beaks showing different feeding modes.",
                    "Discuss how beaks are adapted to the mode of feeding."
                ],
                "conclusion": [
                    "Present drawings of observed mouthparts.",
                    "Discuss the relationship between structure and function in feeding adaptations.",
                    "Write a short report on birds observed during nature walk."
                ],
                "extended": [
                    "Undertake a nature walk to observe different birds and their feeding habits.",
                    "Research about unusual feeding adaptations in animals.",
                    "Create a comparison chart of feeding adaptations."
                ],
                "resources": ["Insect specimens", "Hand lens/dissecting microscope", "Bird images", "Animations of feeding"],
                "assessment": ["Mouthpart drawings", "Nature walk report", "Feeding adaptation presentations"]
            },
            "Animal Transport": {
                "introduction": [
                    "Teacher asks: Why do animals need transport systems?",
                    "Discuss how oxygen and nutrients reach all body parts.",
                    "Show diagrams of different circulatory systems."
                ],
                "development": [
                    "Search for information on transport systems in insects, fish, amphibians, reptiles, and mammals.",
                    "Study illustrations of open and closed circulatory systems.",
                    "Watch animations of the mammalian heart pumping mechanism.",
                    "Dissect a small mammal to observe transport system parts."
                ],
                "conclusion": [
                    "Draw and label transport systems observed.",
                    "Discuss ABO and Rhesus blood grouping systems.",
                    "Prepare charts showing blood donor-recipient compatibility."
                ],
                "extended": [
                    "Visit a health facility to learn about blood grouping.",
                    "Research about blood disorders and their management.",
                    "Create models of different circulatory systems."
                ],
                "resources": ["Illustrations of transport systems", "Animations", "Dissection materials", "Blood typing charts"],
                "assessment": ["System drawings", "Dissection practical", "Blood compatibility charts"]
            },
            "Animal Gaseous Exchange and Respiration": {
                "introduction": [
                    "Teacher asks: How do different animals breathe?",
                    "Discuss characteristics common to all respiratory surfaces.",
                    "Show images of gills, lungs, and tracheal systems."
                ],
                "development": [
                    "Search for information on characteristics of respiratory surfaces.",
                    "Observe images of respiratory structures in different animals.",
                    "Collect locusts and observe spiracles, then draw.",
                    "Dissect a small mammal to observe gaseous exchange structures."
                ],
                "conclusion": [
                    "Make models to demonstrate inhalation and exhalation in humans.",
                    "Discuss how respiratory systems are adapted to different environments.",
                    "Calculate respiratory quotient for various foods."
                ],
                "extended": [
                    "Engage in physical activity and monitor breathing rate changes.",
                    "Research about adaptations for high altitude breathing.",
                    "Compare respiratory efficiency in different animal groups."
                ],
                "resources": ["Images of respiratory systems", "Locusts/grasshoppers", "Dissection materials", "Model-making materials"],
                "assessment": ["Structure drawings", "Dissection practical", "RQ calculations"]
            }
        }
    },
    "Building Construction": {
        "Foundation of Building Construction": {
            "Introduction to Building Construction": {
                "introduction": [
                    "Teacher asks: What is a building and what purposes do buildings serve?",
                    "Brainstorm on the meaning of the term 'building'.",
                    "Show pictures of different types of buildings."
                ],
                "development": [
                    "Use print or digital media to research historical development of buildings.",
                    "Use visual aids to discuss components of a building (floor, wall, roof, door, window).",
                    "Sketch a building showing its basic components.",
                    "Take a walk to observe buildings used for different purposes."
                ],
                "conclusion": [
                    "Present sketches of buildings to the class.",
                    "Create charts listing buildings based on their uses.",
                    "Discuss how building design relates to function."
                ],
                "extended": [
                    "Prepare a portfolio of different types of buildings in your area.",
                    "Research about famous buildings and their architectural features.",
                    "Design your ideal building and explain its features."
                ],
                "resources": ["Print/digital media", "Visual aids", "Charts", "Drawing materials"],
                "assessment": ["Observation schedule", "Written test", "Building sketches"]
            },
            "Site Preparation": {
                "introduction": [
                    "Teacher asks: What must be done before constructing a building?",
                    "Discuss factors to consider when selecting a building site.",
                    "Show images of site clearing and leveling activities."
                ],
                "development": [
                    "Use building code to discuss site selection factors.",
                    "Brainstorm on safety measures for site preparation.",
                    "Use hand tools to carry out site clearing (slasher, panga, jembe, rake).",
                    "Practice site leveling methods (cut, fill, cut and fill)."
                ],
                "conclusion": [
                    "Sketch different methods of leveling a site.",
                    "Debate on the importance of proper site selection.",
                    "Summarize safety precautions for site preparation."
                ],
                "extended": [
                    "Prepare a small site in the school compound.",
                    "Research about modern site preparation equipment.",
                    "Document site preparation process with photographs."
                ],
                "resources": ["Building code", "Hand tools (slasher, panga, jembe, rake, spade)", "Visual aids"],
                "assessment": ["Practical work observation", "Written test", "Site preparation demonstration"]
            }
        },
        "Building Construction Processes": {
            "Concreting": {
                "introduction": [
                    "Teacher displays concrete samples and asks: What is concrete made of?",
                    "Brainstorm on the meaning of concrete.",
                    "Show video of concrete mixing and placing."
                ],
                "development": [
                    "Use media to discuss constituent materials for concrete (cement, sand, aggregates, water).",
                    "Discuss hand tools and equipment for concrete production.",
                    "Learn steps for making concrete (batching, mixing, transporting, placing, compacting, curing).",
                    "Practice making concrete using appropriate tools."
                ],
                "conclusion": [
                    "Present on the importance of concreting in building construction.",
                    "Discuss quality control in concrete production.",
                    "Summarize safety precautions when concreting."
                ],
                "extended": [
                    "Make concrete blocks for a school project.",
                    "Research about different types of concrete (reinforced, prestressed).",
                    "Test concrete samples for strength after curing."
                ],
                "resources": ["Cement", "Sand", "Aggregates", "Water", "Mixing tools", "Safety gear"],
                "assessment": ["Practical observation", "Written test", "Concrete quality assessment"]
            },
            "Foundations": {
                "introduction": [
                    "Teacher asks: Why do buildings need foundations?",
                    "Brainstorm on functions of a foundation.",
                    "Show diagrams of different foundation types."
                ],
                "development": [
                    "Use building code to discuss foundation requirements.",
                    "Use visual aids to discuss foundation types (strip, pad, raft).",
                    "Sketch different types of shallow foundations.",
                    "Set out a strip foundation using 3-4-5 method."
                ],
                "conclusion": [
                    "Present on the importance of foundations in buildings.",
                    "Discuss factors affecting foundation choice.",
                    "Demonstrate proper foundation setting out."
                ],
                "extended": [
                    "Construct a model foundation in the school compound.",
                    "Research about foundation failures and their causes.",
                    "Interview a contractor about foundation construction."
                ],
                "resources": ["Building code", "Drawing tools", "Setting out tools (line, pegs, builder's square)", "Tape measure"],
                "assessment": ["Foundation sketches", "Setting out practical", "Written test"]
            }
        },
        "Building Services": {
            "Plumbing Basics": {
                "introduction": [
                    "Teacher displays plumbing tools and asks learners to identify them.",
                    "Discuss: Why is plumbing important in buildings?",
                    "Show images of plumbing installations."
                ],
                "development": [
                    "Use gallery walk to identify plumbing tools and equipment.",
                    "Search for safety precautions when using plumbing tools.",
                    "Discuss and perform tasks using plumbing tools (cutting, forming, bending).",
                    "Practice care and maintenance of plumbing tools."
                ],
                "conclusion": [
                    "Present on the importance of plumbing tools.",
                    "Demonstrate proper tool maintenance.",
                    "Discuss the role of plumbing in building services."
                ],
                "extended": [
                    "Practice basic pipe jointing techniques.",
                    "Research about modern plumbing materials.",
                    "Design a simple plumbing layout for a room."
                ],
                "resources": ["Plumbing tools (die stock, pipe vice, pipe wrench, cutter)", "Pipes", "Fittings"],
                "assessment": ["Practical observation", "Tool identification test", "Maintenance demonstration"]
            }
        }
    }
}


async def get_substrand_id(subject_name, strand_name, substrand_name):
    """Get substrand ID by navigating through the hierarchy"""
    subject = await db.subjects.find_one({"name": subject_name})
    if not subject:
        return None
    
    strand = await db.strands.find_one({
        "name": {"$regex": strand_name, "$options": "i"},
        "subjectId": str(subject["_id"])
    })
    if not strand:
        return None
    
    substrand = await db.substrands.find_one({
        "name": {"$regex": substrand_name, "$options": "i"},
        "strandId": str(strand["_id"])
    })
    if substrand:
        return str(substrand["_id"])
    return None


async def seed_activities():
    """Seed detailed activities for each substrand"""
    print("=" * 60)
    print("SEEDING DETAILED LEARNING ACTIVITIES")
    print("=" * 60)
    
    activities_added = 0
    activities_updated = 0
    
    for subject_name, strands in ACTIVITIES_DATA.items():
        print(f"\n--- Processing {subject_name} ---")
        
        for strand_name, substrands in strands.items():
            for substrand_name, activity_data in substrands.items():
                substrand_id = await get_substrand_id(subject_name, strand_name, substrand_name)
                
                if not substrand_id:
                    print(f"  [SKIP] Substrand not found: {subject_name} > {strand_name} > {substrand_name}")
                    continue
                
                # Check if activities already exist for this substrand
                existing = await db.learning_activities.find_one({"substrandId": substrand_id})
                
                activity_doc = {
                    "substrandId": substrand_id,
                    "introduction_activities": activity_data.get("introduction", []),
                    "development_activities": activity_data.get("development", []),
                    "conclusion_activities": activity_data.get("conclusion", []),
                    "extended_activities": activity_data.get("extended", []),
                    "learning_resources": activity_data.get("resources", []),
                    "assessment_methods": activity_data.get("assessment", [])
                }
                
                if existing:
                    await db.learning_activities.update_one(
                        {"_id": existing["_id"]},
                        {"$set": activity_doc}
                    )
                    activities_updated += 1
                    print(f"  [UPDATE] {substrand_name}")
                else:
                    await db.learning_activities.insert_one(activity_doc)
                    activities_added += 1
                    print(f"  [ADD] {substrand_name}")
    
    print("\n" + "=" * 60)
    print("ACTIVITIES SEEDING COMPLETE")
    print("=" * 60)
    print(f"Activities Added: {activities_added}")
    print(f"Activities Updated: {activities_updated}")
    print(f"Total: {activities_added + activities_updated}")
    
    # Verify
    total_activities = await db.learning_activities.count_documents({})
    print(f"\nTotal activities in database: {total_activities}")


if __name__ == "__main__":
    asyncio.run(seed_activities())
