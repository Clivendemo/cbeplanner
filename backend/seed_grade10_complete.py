"""
Grade 10 Complete Curriculum Seeding Script
Seeds: Agriculture, Computer Science, Fasihi ya Kiswahili, History and Citizenship, Home Science
Data extracted exactly from KICD Kenya curriculum PDFs (June 2024)

This script:
1. Finds or creates Grade 10
2. Deletes existing data for these subjects
3. Seeds new strands, substrands, SLOs with proper order
4. Creates SLO mappings and learning activities
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
if not mongo_url:
    raise ValueError("MONGO_URL or MONGODB_URI environment variable is required")

client = AsyncIOMotorClient(mongo_url)
db = client['cbeplanner']

# Get reference IDs for competencies, values, PCIs
async def get_reference_ids():
    """Get ObjectIds for standard competencies, values, and PCIs"""
    competencies = {}
    values = {}
    pcis = {}
    
    async for doc in db.competencies.find():
        competencies[doc['name'].lower()] = str(doc['_id'])
    
    async for doc in db.values.find():
        values[doc['name'].lower()] = str(doc['_id'])
    
    async for doc in db.pcis.find():
        pcis[doc['name'].lower()] = str(doc['_id'])
    
    return competencies, values, pcis

def match_competency(name, competencies_map):
    """Match competency name to ID"""
    name_lower = name.lower()
    for key, value in competencies_map.items():
        if key in name_lower or name_lower in key:
            return value
    # Return first if no match
    return list(competencies_map.values())[0] if competencies_map else None

def match_value(name, values_map):
    """Match value name to ID"""
    name_lower = name.lower()
    for key, value in values_map.items():
        if key in name_lower or name_lower in key:
            return value
    return list(values_map.values())[0] if values_map else None

def match_pci(name, pcis_map):
    """Match PCI name to ID"""
    name_lower = name.lower()
    for key, value in pcis_map.items():
        if key in name_lower or name_lower in key:
            return value
    return list(pcis_map.values())[0] if pcis_map else None

async def delete_existing_subject_data(subject_id):
    """Delete all strands, substrands, SLOs, mappings for a subject"""
    subject_id_str = str(subject_id)
    
    # Get all strands for this subject
    strands = await db.strands.find({'subjectId': subject_id_str}).to_list(1000)
    strand_ids = [str(s['_id']) for s in strands]
    
    # Get all substrands
    substrands = await db.substrands.find({'strandId': {'$in': strand_ids}}).to_list(1000)
    substrand_ids = [str(ss['_id']) for ss in substrands]
    substrand_oids = [ss['_id'] for ss in substrands]
    
    # Get all SLOs
    slos = await db.slos.find({'substrandId': {'$in': substrand_ids}}).to_list(1000)
    slo_ids = [str(slo['_id']) for slo in slos]
    
    # Delete SLO mappings
    if slo_ids:
        result = await db.slo_mappings.delete_many({'sloId': {'$in': slo_ids}})
        print(f"    Deleted {result.deleted_count} SLO mappings")
    
    # Delete learning activities
    if substrand_oids:
        result = await db.learning_activities.delete_many({'substrandId': {'$in': substrand_oids}})
        print(f"    Deleted {result.deleted_count} learning activities")
    
    # Delete SLOs
    if substrand_ids:
        result = await db.slos.delete_many({'substrandId': {'$in': substrand_ids}})
        print(f"    Deleted {result.deleted_count} SLOs")
    
    # Delete substrands
    if strand_ids:
        result = await db.substrands.delete_many({'strandId': {'$in': strand_ids}})
        print(f"    Deleted {result.deleted_count} substrands")
    
    # Delete strands
    result = await db.strands.delete_many({'subjectId': subject_id_str})
    print(f"    Deleted {result.deleted_count} strands")

async def seed_subject(subject_name, strands_data, grade_id, comp_map, val_map, pci_map):
    """Seed a complete subject with all its curriculum data"""
    grade_id_str = str(grade_id)
    
    print(f"\n{'='*60}")
    print(f"Seeding: {subject_name}")
    print(f"{'='*60}")
    
    # Find or create subject
    subject = await db.subjects.find_one({'name': subject_name})
    if subject:
        subject_id = subject['_id']
        # Ensure grade is in gradeIds
        if grade_id_str not in subject.get('gradeIds', []):
            await db.subjects.update_one(
                {'_id': subject_id},
                {'$addToSet': {'gradeIds': grade_id_str}}
            )
        print(f"  Found existing subject: {subject_name}")
        # Delete existing data
        await delete_existing_subject_data(subject_id)
    else:
        result = await db.subjects.insert_one({
            'name': subject_name,
            'gradeIds': [grade_id_str]
        })
        subject_id = result.inserted_id
        print(f"  Created new subject: {subject_name}")
    
    subject_id_str = str(subject_id)
    
    total_strands = 0
    total_substrands = 0
    total_slos = 0
    total_mappings = 0
    total_activities = 0
    
    # Seed strands in order
    for strand_data in strands_data:
        strand_result = await db.strands.insert_one({
            'name': strand_data['name'],
            'subjectId': subject_id_str
        })
        strand_id = strand_result.inserted_id
        strand_id_str = str(strand_id)
        total_strands += 1
        print(f"    Created Strand: {strand_data['name']}")
        
        # Seed substrands in order
        for substrand_data in strand_data.get('substrands', []):
            substrand_result = await db.substrands.insert_one({
                'name': substrand_data['name'],
                'strandId': strand_id_str
            })
            substrand_id = substrand_result.inserted_id
            substrand_id_str = str(substrand_id)
            total_substrands += 1
            
            # Collect all learning experiences for this substrand
            all_learning_experiences = []
            all_inquiry_questions = []
            
            # Seed SLOs in order
            for slo_data in substrand_data.get('slos', []):
                slo_result = await db.slos.insert_one({
                    'name': slo_data['name'],
                    'description': slo_data.get('description', slo_data['name']),
                    'substrandId': substrand_id_str
                })
                slo_id = slo_result.inserted_id
                slo_id_str = str(slo_id)
                total_slos += 1
                
                # Collect learning experiences
                all_learning_experiences.extend(slo_data.get('learning_experiences', []))
                all_inquiry_questions.extend(slo_data.get('inquiry_questions', []))
                
                # Create SLO mapping
                competency_ids = []
                for comp_name in slo_data.get('competencies', []):
                    comp_id = match_competency(comp_name, comp_map)
                    if comp_id:
                        competency_ids.append(comp_id)
                
                value_ids = []
                for val_name in slo_data.get('values', []):
                    val_id = match_value(val_name, val_map)
                    if val_id:
                        value_ids.append(val_id)
                
                pci_ids = []
                for pci_name in slo_data.get('pcis', []):
                    pci_id = match_pci(pci_name, pci_map)
                    if pci_id:
                        pci_ids.append(pci_id)
                
                await db.slo_mappings.insert_one({
                    'sloId': slo_id_str,
                    'competencyIds': competency_ids[:3] if competency_ids else [],
                    'valueIds': value_ids[:3] if value_ids else [],
                    'pciIds': pci_ids[:3] if pci_ids else [],
                    'assessmentIds': []
                })
                total_mappings += 1
            
            # Create learning activity for this substrand
            if all_learning_experiences:
                # Split into intro, development, conclusion
                num_exp = len(all_learning_experiences)
                intro_count = max(1, num_exp // 4)
                dev_count = max(1, num_exp // 2)
                
                await db.learning_activities.insert_one({
                    'substrandId': substrand_id,  # ObjectId for learning_activities
                    'introduction_activities': all_learning_experiences[:intro_count],
                    'development_activities': all_learning_experiences[intro_count:intro_count + dev_count],
                    'conclusion_activities': all_learning_experiences[intro_count + dev_count:],
                    'extended_activities': all_inquiry_questions[:2] if all_inquiry_questions else [],
                    'learning_resources': ['Digital devices', 'Textbooks', 'Resource persons', 'Field trips'],
                    'assessment_methods': ['Observation', 'Written tests', 'Oral questions', 'Project work']
                })
                total_activities += 1
    
    print(f"\n  Summary for {subject_name}:")
    print(f"    - Strands: {total_strands}")
    print(f"    - Substrands: {total_substrands}")
    print(f"    - SLOs: {total_slos}")
    print(f"    - SLO Mappings: {total_mappings}")
    print(f"    - Learning Activities: {total_activities}")
    
    return total_strands, total_substrands, total_slos, total_mappings

# ============================================================================
# SUBJECT DATA DEFINITIONS
# ============================================================================

# AGRICULTURE - Grade 10
AGRICULTURE_STRANDS = [
    {
        "name": "Crop Production",
        "substrands": [
            {
                "name": "Agricultural Land",
                "slos": [
                    {"name": "Describe ways of accessing land for agricultural use", "description": "By the end of the sub strand the learner should be able to describe ways of accessing land for agricultural use including leasing, inheriting, buying and donation", "learning_experiences": ["Discuss with resource person ways of accessing land for agricultural use", "Take an excursion in the community to study and assess different forms of land", "Use digital devices to search for information on natural factors that determine productivity of land", "Make class presentations on importance of land in agricultural production"], "inquiry_questions": ["How is land productivity determined for agriculture?", "Why is land put into different agricultural uses?"], "competencies": ["Citizenship", "Communication and Collaboration"], "pcis": ["Environmental Education"], "values": ["Respect", "Social Justice"]},
                    {"name": "Evaluate utility of land for agricultural production", "description": "By the end of the sub strand the learner should be able to evaluate utility of land for agricultural production purposes", "learning_experiences": ["Take an excursion to study and assess different forms of land"], "inquiry_questions": ["Why is land put into different agricultural uses?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Environmental Education"], "values": ["Responsibility"]},
                    {"name": "Analyse natural factors that determine productivity of land", "description": "By the end of the sub strand the learner should be able to analyse natural factors that determine productivity of land in agriculture", "learning_experiences": ["Use digital devices to search for information on natural factors"], "inquiry_questions": ["How is land productivity determined?"], "competencies": ["Digital Literacy"], "pcis": ["Environmental Education"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Properties of Soil",
                "slos": [
                    {"name": "Describe properties of soil for crop production", "description": "By the end of the sub strand the learner should be able to describe properties of a soil for crop production", "learning_experiences": ["Discuss on physical, chemical and biological properties of soil", "Conduct experiments to test physical properties (porosity, texture)", "Take field excursion to observe soil profile", "Use digital resources to search for importance of soil properties"], "inquiry_questions": ["How do properties of soil influence crop production?"], "competencies": ["Digital Literacy", "Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Unity", "Respect"]},
                    {"name": "Investigate properties of soil for crop production", "description": "By the end of the sub strand the learner should be able to investigate the properties of soil through experiments", "learning_experiences": ["Conduct experiments to test physical, chemical and biological properties"], "inquiry_questions": ["How do properties of soil influence crop production?"], "competencies": ["Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Unity"]},
                    {"name": "Relate soil profile to crop production", "description": "By the end of the sub strand the learner should be able to relate importance of soil profile to crop production", "learning_experiences": ["Take field excursion to observe and relate soil profile to farming"], "inquiry_questions": ["How do properties of soil influence crop production?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Environmental Education"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Land Preparation",
                "slos": [
                    {"name": "Describe activities of fallow land preparation", "description": "By the end of the sub strand the learner should be able to describe activities of fallow land preparation to appropriate seedbed", "learning_experiences": ["Brainstorm on activities carried out on fallow land", "Carry out applicable activities on fallow land", "Apply conservation tillage practices", "Make presentations on importance of proper land preparation"], "inquiry_questions": ["How does proper land preparation contribute to crop production?"], "competencies": ["Critical Thinking and Problem Solving", "Citizenship"], "pcis": ["Life Skills", "Safety and Security"], "values": ["Peace", "Unity"]},
                    {"name": "Carry out land preparation operations", "description": "By the end of the sub strand the learner should be able to carry out land preparation operations for selected crop", "learning_experiences": ["Carry out applicable activities on fallow land to prepare seedbed"], "inquiry_questions": ["How does proper land preparation contribute to crop production?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Apply conservation tillage in crop production", "description": "By the end of the sub strand the learner should be able to apply conservation tillage in crop production", "learning_experiences": ["Apply conservation tillage practices such as zero tillage and minimum tillage"], "inquiry_questions": ["How does proper land preparation contribute to crop production?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Environmental Education"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Field Management Practices",
                "slos": [
                    {"name": "Describe management practices of crops", "description": "By the end of the sub strand the learner should be able to describe management practices of selected vegetable and perennial crops", "learning_experiences": ["Use digital devices to study pruning of vegetables", "Carry out pruning of selected vegetable crops", "Discuss and carry out top dressing of selected crops", "Make a field trip to study field management practices"], "inquiry_questions": ["How do field management practices influence crop production?"], "competencies": ["Communication and Collaboration", "Self-Efficacy"], "pcis": ["Financial Literacy", "Environmental Education"], "values": ["Respect", "Responsibility"]},
                    {"name": "Carry out selected management practices", "description": "By the end of the sub strand the learner should be able to carry out selected management practices in crop production", "learning_experiences": ["Carry out pruning and top dressing of crops"], "inquiry_questions": ["How do field management practices influence crop production?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Growing Selected Crops",
                "slos": [
                    {"name": "Determine crops established through nursery", "description": "By the end of the sub strand the learner should be able to determine crops that are established through the nursery", "learning_experiences": ["Brainstorm to determine appropriate crops for nursery establishment", "Establish and carry out appropriate management practices", "Make class presentations on field management practices"], "inquiry_questions": ["How do management practices influence crop productivity?"], "competencies": ["Creativity and Imagination", "Self-Efficacy"], "pcis": ["Learner Support Programme", "Safety and Security"], "values": ["Responsibility", "Respect"]},
                    {"name": "Grow a selected crop applying appropriate management", "description": "By the end of the sub strand the learner should be able to grow a selected crop applying appropriate management practices", "learning_experiences": ["Establish and carry out appropriate management practices for selected crop"], "inquiry_questions": ["How do management practices influence crop productivity?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Crop Protection",
                "slos": [
                    {"name": "Identify weeds in a crop field", "description": "By the end of the sub strand the learner should be able to identify weeds in a crop field", "learning_experiences": ["Take excursion to identify weeds and make herbarium", "Use digital resources to classify weeds", "Discuss methods of weed control", "Carry out weed control in a crop field", "Make presentations on pros and cons of weeds"], "inquiry_questions": ["How do weeds affect crop production?", "Why is weed control done?"], "competencies": ["Digital Literacy", "Learning to Learn"], "pcis": ["Financial Literacy", "Learner Support Programme"], "values": ["Responsibility", "Respect"]},
                    {"name": "Classify weeds based on provided criteria", "description": "By the end of the sub strand the learner should be able to classify weeds based on morphology and life cycle", "learning_experiences": ["Use digital resources to classify weeds"], "inquiry_questions": ["How do weeds affect crop production?"], "competencies": ["Digital Literacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Describe methods of weed control", "description": "By the end of the sub strand the learner should be able to describe methods of weed control", "learning_experiences": ["Discuss methods of weed control including physical, cultural, biological, chemical"], "inquiry_questions": ["Why is weed control done in crop production?"], "competencies": ["Communication and Collaboration"], "pcis": ["Life Skills"], "values": ["Unity"]},
                    {"name": "Carry out weed control", "description": "By the end of the sub strand the learner should be able to carry out weed control using appropriate methods", "learning_experiences": ["Carry out weed control in a crop field"], "inquiry_questions": ["Why is weed control done?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "General Crop Harvesting",
                "slos": [
                    {"name": "Explain factors that determine harvesting", "description": "By the end of the sub strand the learner should be able to explain factors that determine harvesting of crop produce", "learning_experiences": ["Discuss factors that determine harvesting including timing, stage of growth, purpose", "Carry out harvesting process for tubers and cereals", "Discuss importance of harvesting process"], "inquiry_questions": ["How does harvesting process affect quantity and quality of crop produce?"], "competencies": ["Citizenship", "Critical Thinking and Problem Solving"], "pcis": ["Life Skills", "Learner Support Programme"], "values": ["Integrity", "Unity"]},
                    {"name": "Carry out the harvesting process", "description": "By the end of the sub strand the learner should be able to carry out the harvesting process for selected crop produce", "learning_experiences": ["Carry out pre-harvest, harvesting and post-harvest practices"], "inquiry_questions": ["How does harvesting process affect quantity and quality?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            }
        ]
    },
    {
        "name": "Animal Production",
        "substrands": [
            {
                "name": "Breeds of Livestock",
                "slos": [
                    {"name": "Describe breeds of livestock based on uses", "description": "By the end of the sub strand the learner should be able to describe breeds of livestock based on their uses", "learning_experiences": ["Use digital and print resources to describe breeds of cattle, pigs, rabbits, sheep and goats", "Take field trip to distinguish common breed livestock", "Discuss comparative productivity from various livestock breeds"], "inquiry_questions": ["How does livestock breeds affect productivity of animals?"], "competencies": ["Digital Literacy", "Communication and Collaboration"], "pcis": ["Financial Literacy", "Safety and Security"], "values": ["Unity", "Respect"]},
                    {"name": "Distinguish common breed livestock", "description": "By the end of the sub strand the learner should be able to distinguish common breed livestock based on their characteristics", "learning_experiences": ["Take field trip to distinguish common breed livestock"], "inquiry_questions": ["How does livestock breeds affect productivity?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            },
            {
                "name": "Animal Handling and Safety",
                "slos": [
                    {"name": "Examine forms of animal handling", "description": "By the end of the sub strand the learner should be able to examine forms of animal handling in the community", "learning_experiences": ["Discuss inhumane treatments such as beating, poor restraining", "Use digital devices to observe structures for safe handling", "Discuss ways of ensuring safety of persons handling animals", "Use tools for animal safety including halter, restraining rope, bull ring", "Take excursion to observe animal handling"], "inquiry_questions": ["How can we ensure safety when handling animals?"], "competencies": ["Citizenship"], "pcis": ["Safety and Security"], "values": ["Love"]},
                    {"name": "Describe structures for safe handling of animals", "description": "By the end of the sub strand the learner should be able to describe structures used to ensure safety in handling domestic animals", "learning_experiences": ["Use digital devices to observe structures for safe handling"], "inquiry_questions": ["How can we ensure safety?"], "competencies": ["Digital Literacy"], "pcis": ["Safety and Security"], "values": ["Responsibility"]},
                    {"name": "Use tools and equipment for animal safety", "description": "By the end of the sub strand the learner should be able to use tools and equipment to ensure safety in handling domestic animals", "learning_experiences": ["Use halter, restraining rope, bull ring and lead stick for animal safety"], "inquiry_questions": ["How can we ensure safety?"], "competencies": ["Self-Efficacy"], "pcis": ["Safety and Security"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "General Animal Health",
                "slos": [
                    {"name": "Explain benefits of keeping animals healthy", "description": "By the end of the sub strand the learner should be able to explain the benefits of keeping animals healthy in livestock production", "learning_experiences": ["Use digital and print resources to explain benefits of keeping animals healthy", "Discuss with resource person to identify signs of ill health", "Discuss preventative and control measures of ill health", "Practise measures that maintain animal health"], "inquiry_questions": ["How is animal health important in animal production?"], "competencies": ["Citizenship", "Creativity and Imagination"], "pcis": ["Life Skills", "Health Education"], "values": ["Patriotism", "Integrity"]},
                    {"name": "Identify signs of ill health in livestock", "description": "By the end of the sub strand the learner should be able to identify signs of ill health in livestock production", "learning_experiences": ["Discuss with resource person and observe animals to identify signs of ill health"], "inquiry_questions": ["How is animal health important?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Health Education"], "values": ["Responsibility"]},
                    {"name": "Propose general control measures of ill health", "description": "By the end of the sub strand the learner should be able to propose general control measures of ill health in livestock production", "learning_experiences": ["Discuss preventative and control measures"], "inquiry_questions": ["How is animal health important?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Health Education"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Bee Keeping",
                "slos": [
                    {"name": "Explain factors to consider in siting an apiary", "description": "By the end of the sub strand the learner should be able to explain the factors to consider in siting an apiary", "learning_experiences": ["Discuss factors to consider in siting an apiary", "Use digital devices to acquire information on how to stock a hive", "Participate in safe apiary management practices", "Role play honey harvesting process using empty hive"], "inquiry_questions": ["How are bees reared?"], "competencies": ["Digital Literacy", "Self-Efficacy"], "pcis": ["Health Education", "Safety and Security"], "values": ["Responsibility", "Unity"]},
                    {"name": "Describe the process of stocking a hive", "description": "By the end of the sub strand the learner should be able to describe the process of stocking a hive", "learning_experiences": ["Use digital devices to acquire information on stocking a hive"], "inquiry_questions": ["How are bees reared?"], "competencies": ["Digital Literacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Carry out safe apiary management practices", "description": "By the end of the sub strand the learner should be able to carry out safe apiary management practices", "learning_experiences": ["Participate in guided process of apiary management"], "inquiry_questions": ["How are bees reared?"], "competencies": ["Self-Efficacy"], "pcis": ["Safety and Security"], "values": ["Responsibility"]},
                    {"name": "Demonstrate honey harvesting process", "description": "By the end of the sub strand the learner should be able to demonstrate honey harvesting process", "learning_experiences": ["Use empty hive to role play honey harvesting"], "inquiry_questions": ["How are bees reared?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Unity"]}
                ]
            },
            {
                "name": "Animal Rearing Project",
                "slos": [
                    {"name": "Develop a project plan on rearing a selected animal", "description": "By the end of the sub strand the learner should be able to develop a project plan on rearing a selected animal", "learning_experiences": ["Adopt a project template to write a project plan", "Brainstorm on appropriate animal rearing project and budget", "Select site and install required structures", "Stock and manage the animal project", "Make class presentations on success and improvements"], "inquiry_questions": ["How can animal rearing project be carried out?"], "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"], "pcis": ["Learner Support Programme", "Financial Literacy"], "values": ["Love", "Social Justice"]},
                    {"name": "Prepare a budget for the animal rearing project", "description": "By the end of the sub strand the learner should be able to prepare a budget for the animal rearing project", "learning_experiences": ["Develop project details and simple budget"], "inquiry_questions": ["How can animal rearing project be carried out?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Financial Literacy"], "values": ["Responsibility"]},
                    {"name": "Implement the plan for the animal rearing project", "description": "By the end of the sub strand the learner should be able to implement the plan for the animal rearing project", "learning_experiences": ["Select site, install structures, prepare record templates"], "inquiry_questions": ["How can animal rearing project be carried out?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Carry out routine management practices", "description": "By the end of the sub strand the learner should be able to carry out routine management practices on the animal rearing project", "learning_experiences": ["Stock and manage the animal project as per plan"], "inquiry_questions": ["How can animal rearing project be carried out?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Evaluate the animal rearing practices", "description": "By the end of the sub strand the learner should be able to evaluate the animal rearing practices carried out in the project", "learning_experiences": ["Make class presentations on success and areas of improvement"], "inquiry_questions": ["How can animal rearing project be carried out?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Integrity"]}
                ]
            }
        ]
    },
    {
        "name": "Agricultural Technologies and Entrepreneurship",
        "substrands": [
            {
                "name": "Tools and Equipment",
                "slos": [
                    {"name": "Identify tools and equipment for agricultural tasks", "description": "By the end of the sub strand the learner should be able to identify tools and equipment used for various agricultural tasks", "learning_experiences": ["Observe and analyse tools and equipment for agricultural tasks", "Conduct various agricultural tasks using appropriate tools", "Carry out maintenance practices on tools and equipment", "Practise care and safety in use of tools", "Discuss importance of maintaining tools"], "inquiry_questions": ["How do tools and equipment contribute to efficiency of farm operations?"], "competencies": ["Self-Efficacy", "Creativity and Imagination"], "pcis": ["Health Education", "Safety and Security"], "values": ["Responsibility", "Respect"]},
                    {"name": "Carry out maintenance practices on tools", "description": "By the end of the sub strand the learner should be able to carry out appropriate maintenance practices on selected tools and equipment", "learning_experiences": ["Carry out cleaning, sharpening, lubrication, repairs on tools"], "inquiry_questions": ["How do tools contribute to efficiency?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Apply safety measures in use of tools", "description": "By the end of the sub strand the learner should be able to apply safety measures in the use of tools and equipment", "learning_experiences": ["Practise appropriate storage, correct usage, safe distance"], "inquiry_questions": ["How do tools contribute to efficiency?"], "competencies": ["Self-Efficacy"], "pcis": ["Safety and Security"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Product Processing and Value Addition",
                "slos": [
                    {"name": "Suggest methods of value addition", "description": "By the end of the sub strand the learner should be able to suggest methods of value addition for selected agricultural produce", "learning_experiences": ["Use digital resources to suggest value addition methods", "Discuss processing of plant origin produce into jam, butter, juices", "Discuss processing of animal origin produce like honey, milk", "Visit market outlets to study packaging and branding", "Discuss ethical concerns in processing"], "inquiry_questions": ["How does value addition enhance nutrition and food security?"], "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"], "pcis": ["Life Skills", "Health Education", "Financial Literacy"], "values": ["Responsibility", "Peace"]},
                    {"name": "Carry out processing of plant origin produce", "description": "By the end of the sub strand the learner should be able to carry out processing of agricultural produce of plant origin", "learning_experiences": ["Process vegetables, fruits, cereals into jam, ketchup, flour"], "inquiry_questions": ["How does value addition enhance nutrition?"], "competencies": ["Self-Efficacy"], "pcis": ["Health Education"], "values": ["Responsibility"]},
                    {"name": "Carry out processing of animal origin produce", "description": "By the end of the sub strand the learner should be able to carry out processing of agricultural produce of animal origin", "learning_experiences": ["Process honey, milk, hides and skins, meat"], "inquiry_questions": ["How does value addition enhance nutrition?"], "competencies": ["Self-Efficacy"], "pcis": ["Health Education"], "values": ["Responsibility"]},
                    {"name": "Carry out home-based packaging and branding", "description": "By the end of the sub strand the learner should be able to carry out home-based packaging and branding of processed agricultural products", "learning_experiences": ["Visit market outlets to study packaging and branding methods"], "inquiry_questions": ["How does value addition enhance food security?"], "competencies": ["Creativity and Imagination"], "pcis": ["Financial Literacy"], "values": ["Integrity"]}
                ]
            },
            {
                "name": "Establishing Agricultural Enterprise",
                "slos": [
                    {"name": "Explain factors of production in agricultural enterprise", "description": "By the end of the sub strand the learner should be able to explain factors of production in an agricultural enterprise", "learning_experiences": ["Discuss factors of production: land, labour, entrepreneurship, capital", "Discuss ways of mobilizing capital for enterprise", "Search for factors to consider in selecting an enterprise", "Evaluate sources of support services", "Present role of various factors of production"], "inquiry_questions": ["How do we establish an agricultural enterprise?"], "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"], "pcis": ["Financial Literacy", "Learner Support Programme"], "values": ["Patriotism", "Respect"]},
                    {"name": "Propose ways of acquiring capital", "description": "By the end of the sub strand the learner should be able to propose ways of acquiring capital to establish an agricultural enterprise", "learning_experiences": ["Discuss borrowing, savings, disposing assets, grants"], "inquiry_questions": ["How do we establish an enterprise?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Financial Literacy"], "values": ["Responsibility"]},
                    {"name": "Examine factors in selecting agricultural enterprise", "description": "By the end of the sub strand the learner should be able to examine factors to consider in selecting an agricultural enterprise", "learning_experiences": ["Use digital resources to examine factors for selecting enterprise"], "inquiry_questions": ["How do we establish an enterprise?"], "competencies": ["Digital Literacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Evaluate sources of support services", "description": "By the end of the sub strand the learner should be able to evaluate sources of support services for agricultural enterprise", "learning_experiences": ["Discuss with resource person to evaluate support services"], "inquiry_questions": ["How do we establish an enterprise?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            },
            {
                "name": "Marketing Agricultural Produce",
                "slos": [
                    {"name": "Describe ways of preparing produce for marketing", "description": "By the end of the sub strand the learner should be able to describe ways of preparing agricultural produce for marketing", "learning_experiences": ["Discuss weighing, sorting, grading, packaging, branding, labeling", "Visit agricultural market outlet to observe marketing processes", "Demonstrate how to prepare samples for marketing", "Discuss market outlets including digital and physical", "Inquire about expenses in marketing activities"], "inquiry_questions": ["How can we prepare agricultural produce for the market?"], "competencies": ["Self-Efficacy"], "pcis": ["Financial Literacy"], "values": ["Integrity"]},
                    {"name": "Discuss market outlets for agricultural produce", "description": "By the end of the sub strand the learner should be able to discuss market outlets for agricultural produce", "learning_experiences": ["Discuss digital platforms and physical market outlets"], "inquiry_questions": ["How can we prepare produce for market?"], "competencies": ["Digital Literacy"], "pcis": ["Financial Literacy"], "values": ["Responsibility"]},
                    {"name": "Evaluate expenses in marketing agricultural produce", "description": "By the end of the sub strand the learner should be able to evaluate expenses incurred in marketing agricultural produce", "learning_experiences": ["Inquire about transportation, advertisement, market charges, taxes"], "inquiry_questions": ["How can we prepare produce for market?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Financial Literacy"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Composting Techniques",
                "slos": [
                    {"name": "Describe composting in production of organic manure", "description": "By the end of the sub strand the learner should be able to describe composting in production of organic manure", "learning_experiences": ["Use digital resources to describe composting methods", "Discuss factors that influence quality of compost manure", "Follow procedure to carry out pit and heap composting", "Carry out innovative composting like vermi-composting", "Utilize compost manure to existing crop enterprises"], "inquiry_questions": ["Why is composting relevant in soil improvement?"], "competencies": ["Digital Literacy", "Creativity and Imagination"], "pcis": ["Learner Support Programme", "Environmental Education"], "values": ["Responsibility", "Respect"]},
                    {"name": "Examine factors that influence quality of compost", "description": "By the end of the sub strand the learner should be able to examine factors that influence quality of compost manure", "learning_experiences": ["Discuss factors: materials, process, storage"], "inquiry_questions": ["Why is composting relevant?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Environmental Education"], "values": ["Responsibility"]},
                    {"name": "Carry out conventional composting methods", "description": "By the end of the sub strand the learner should be able to carry out conventional composting methods for production of organic manure", "learning_experiences": ["Follow procedure for pit and heap composting methods"], "inquiry_questions": ["Why is composting relevant?"], "competencies": ["Self-Efficacy"], "pcis": ["Environmental Education"], "values": ["Responsibility"]},
                    {"name": "Carry out innovative composting methods", "description": "By the end of the sub strand the learner should be able to carry out innovative composting methods for production of organic manure", "learning_experiences": ["Carry out vermi-composting and containerized composting"], "inquiry_questions": ["Why is composting relevant?"], "competencies": ["Creativity and Imagination", "Digital Literacy"], "pcis": ["Environmental Education"], "values": ["Responsibility"]}
                ]
            }
        ]
    }
]

# COMPUTER SCIENCE - Grade 10
COMPUTER_SCIENCE_STRANDS = [
    {
        "name": "Foundation of Computer Science",
        "substrands": [
            {
                "name": "Evolution and Development of Computers",
                "slos": [
                    {"name": "Identify early computing devices", "description": "By the end of the sub strand the learner should be able to identify early computing devices and how they relate to evolution of electronic computers", "learning_experiences": ["Search for information on ancient computing devices like Abacus, Pascaline, Slide Rule", "Search for information on principle technologies that defined development of computers", "Discuss various generations of computers", "Match different generations to their principal technologies"], "inquiry_questions": ["How have computers evolved over time?"], "competencies": ["Communication and Collaboration", "Self-Efficacy"], "pcis": ["Citizenship Education"], "values": ["Unity", "Responsibility"]},
                    {"name": "Describe principle technologies in computer development", "description": "By the end of the sub strand the learner should be able to describe principle technologies that defined development of computers", "learning_experiences": ["Search for information on vacuum tubes, transistors, integrated circuits"], "inquiry_questions": ["How have computers evolved?"], "competencies": ["Digital Literacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Relate technologies to computer generations", "description": "By the end of the sub strand the learner should be able to relate the principle technologies to respective computer generation", "learning_experiences": ["Match different generations of computers to their technologies"], "inquiry_questions": ["How have computers evolved?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Unity"]}
                ]
            },
            {
                "name": "Computer Organisation and Architecture",
                "slos": [
                    {"name": "Describe von Neumann computer architecture", "description": "By the end of the sub strand the learner should be able to describe the functional organisation and architecture of a von Neumann computer", "learning_experiences": ["Search for information on structure of von Neumann computer architecture", "Brainstorm on RISC and CISC architectures", "Illustrate organisation among functional elements", "Watch video of fetch-execute cycle", "Make a model computer architecture"], "inquiry_questions": ["How is a computer organised internally?"], "competencies": ["Critical Thinking and Problem Solving", "Digital Literacy"], "pcis": ["Life Skills"], "values": ["Respect", "Unity"]},
                    {"name": "Analyse relationships among functional elements", "description": "By the end of the sub strand the learner should be able to analyse the relationships among functional elements of von Neumann computer", "learning_experiences": ["Illustrate organisation among functional elements including CPU, storage, buses"], "inquiry_questions": ["How is a computer organised?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]},
                    {"name": "Create a model of computer architecture", "description": "By the end of the sub strand the learner should be able to create a model of a computer architecture depicting the structural elements", "learning_experiences": ["Make a model computer architecture with all structural elements"], "inquiry_questions": ["How is a computer organised?"], "competencies": ["Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Unity"]},
                    {"name": "Use number systems to represent data", "description": "By the end of the sub strand the learner should be able to use binary, octal and hexadecimal number systems to represent data", "learning_experiences": ["Convert numbers from base ten to binary, octal and hexadecimal"], "inquiry_questions": ["How is data represented in computers?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Input/Output (I/O) Devices",
                "slos": [
                    {"name": "Describe types of input and output devices", "description": "By the end of the sub strand the learner should be able to describe types of input and output devices used in computer systems", "learning_experiences": ["Discuss types of input devices including keying, pointing, scanning devices", "Search for information on output devices including printers, monitors, speakers", "Create a QR code and share information", "Scan a document and share with peers", "Visit computer user environment to identify I/O devices"], "inquiry_questions": ["What are the different types of I/O devices?"], "competencies": ["Creativity and Imagination", "Learning to Learn"], "pcis": ["Environmental Education"], "values": ["Peace", "Unity"]},
                    {"name": "Examine criteria for selecting I/O devices", "description": "By the end of the sub strand the learner should be able to examine criteria used in selecting input and output devices", "learning_experiences": ["Brainstorm on factors to consider when acquiring I/O devices"], "inquiry_questions": ["How do we select I/O devices?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Financial Literacy"], "values": ["Responsibility"]},
                    {"name": "Use input and output devices to perform tasks", "description": "By the end of the sub strand the learner should be able to use input and output devices to perform tasks", "learning_experiences": ["Create QR codes, scan documents, share with peers"], "inquiry_questions": ["How do we use I/O devices?"], "competencies": ["Digital Literacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Computer Storage",
                "slos": [
                    {"name": "Identify types of storage in computer systems", "description": "By the end of the sub strand the learner should be able to identify types of storage used in computer systems", "learning_experiences": ["Share experiences on types of storage devices", "Discuss categories of computer storage: primary and secondary", "Discuss types of RAM and ROM", "Save, transfer and retrieve data from computer storage", "Debate on benefits of remote versus local storage"], "inquiry_questions": ["What are the different types of computer storage?"], "competencies": ["Communication and Collaboration", "Self-Efficacy"], "pcis": ["Environmental Education"], "values": ["Responsibility", "Patriotism"]},
                    {"name": "Categorise types of storage", "description": "By the end of the sub strand the learner should be able to categorise types of storage used in computer systems", "learning_experiences": ["Discuss and classify secondary storage into internal and external"], "inquiry_questions": ["How do we categorise storage?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Read and write data to computer storage", "description": "By the end of the sub strand the learner should be able to read data from and write data to a computer storage", "learning_experiences": ["Save, transfer and retrieve data from storage"], "inquiry_questions": ["How do we use computer storage?"], "competencies": ["Digital Literacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Establish criteria for selecting computer storage", "description": "By the end of the sub strand the learner should be able to establish criteria used to select computer storage", "learning_experiences": ["Carry out case study to compare types of storage in terms of capacity, portability"], "inquiry_questions": ["How do we select storage?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Financial Literacy"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Central Processing Unit (CPU)",
                "slos": [
                    {"name": "Describe structural elements of CPU", "description": "By the end of the sub strand the learner should be able to describe structural elements of the CPU of a computer system", "learning_experiences": ["Brainstorm on structural elements of CPU", "Watch video simulation of CPU elements", "Discuss functions of ALU, control unit, registers, buses", "Draw diagram of fetch-decode-execute cycle", "Compare types of CPU in computing devices"], "inquiry_questions": ["What are the components of a CPU?"], "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Unity", "Respect"]},
                    {"name": "Relate CPU elements to their functions", "description": "By the end of the sub strand the learner should be able to relate structural elements of the CPU to their functions", "learning_experiences": ["Discuss functions of ALU, control unit, registers, buses"], "inquiry_questions": ["What do CPU components do?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]},
                    {"name": "Examine types of CPUs in computing devices", "description": "By the end of the sub strand the learner should be able to examine types of CPUs in computing devices", "learning_experiences": ["Compare types of CPU according to instruction set, word length, core design"], "inquiry_questions": ["What types of CPUs exist?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Operating System (OS)",
                "slos": [
                    {"name": "Describe functions of an operating system", "description": "By the end of the sub strand the learner should be able to describe functions of an operating system", "learning_experiences": ["Search for definition of operating system and examples", "Discuss functions including booting, resource management, memory management", "Visit computer user environment to observe available OS", "Classify OS according to tasks, users, and user interface", "Install OS in a virtual environment"], "inquiry_questions": ["What are the functions of an operating system?"], "competencies": ["Critical Thinking and Problem Solving", "Learning to Learn"], "pcis": ["Life Skills"], "values": ["Respect", "Integrity"]},
                    {"name": "Classify operating systems by attributes", "description": "By the end of the sub strand the learner should be able to classify operating system according to different attributes", "learning_experiences": ["Classify OS according to tasks, users, user interface"], "inquiry_questions": ["How do we classify operating systems?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]},
                    {"name": "Install an operating system", "description": "By the end of the sub strand the learner should be able to install an operating system in a computer", "learning_experiences": ["Install different types of OS in a virtual environment"], "inquiry_questions": ["How do we install an OS?"], "competencies": ["Digital Literacy", "Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Integrity"]},
                    {"name": "Use an operating system to perform tasks", "description": "By the end of the sub strand the learner should be able to use an operating system to perform a task", "learning_experiences": ["Use OS to manipulate files and folders"], "inquiry_questions": ["How do we use an OS?"], "competencies": ["Digital Literacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Computer Setup",
                "slos": [
                    {"name": "Explain types of ports and cables", "description": "By the end of the sub strand the learner should be able to explain types of ports and cables used in computers", "learning_experiences": ["Search for information on cables and ports", "Discuss types of cables and ports used", "Match ports to corresponding cables", "Discuss safety precautions in setting up computer", "Connect cables to ports and set up computer"], "inquiry_questions": ["What types of ports and cables are used in computers?"], "competencies": ["Digital Literacy", "Self-Efficacy"], "pcis": ["Environmental Education"], "values": ["Integrity", "Responsibility"]},
                    {"name": "Relate cables to corresponding ports", "description": "By the end of the sub strand the learner should be able to relate cables to their corresponding ports in a computer", "learning_experiences": ["Take turns to match ports to their corresponding cables"], "inquiry_questions": ["How do cables connect to ports?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Set up a computer for use", "description": "By the end of the sub strand the learner should be able to set up a computer for use", "learning_experiences": ["Connect all parts of a computer and use it to perform a task"], "inquiry_questions": ["How do we set up a computer?"], "competencies": ["Digital Literacy", "Self-Efficacy"], "pcis": ["Safety and Security"], "values": ["Responsibility"]}
                ]
            }
        ]
    },
    {
        "name": "Computer Networking",
        "substrands": [
            {
                "name": "Data Communication",
                "slos": [
                    {"name": "Define basic data communications concepts", "description": "By the end of the sub strand the learner should be able to define basic data communications concepts", "learning_experiences": ["Search for definitions of data, signals, network, protocols, OSI model", "Discuss characteristics of data communication", "Create simulation to show interaction among components", "Illustrate data communication modes: simplex, half-duplex, full-duplex"], "inquiry_questions": ["What are the fundamentals of data communication?"], "competencies": ["Self-Efficacy", "Communication and Collaboration"], "pcis": ["Life Skills"], "values": ["Patriotism", "Respect"]},
                    {"name": "Describe characteristics of data communication", "description": "By the end of the sub strand the learner should be able to describe characteristics of data communication in computer networking", "learning_experiences": ["Discuss characteristics of data communication"], "inquiry_questions": ["What are characteristics of data communication?"], "competencies": ["Communication and Collaboration"], "pcis": ["Life Skills"], "values": ["Respect"]},
                    {"name": "Analyse components of data communication system", "description": "By the end of the sub strand the learner should be able to analyse the components of data communication system", "learning_experiences": ["Create simulation showing sender, message, medium, protocol, receiver"], "inquiry_questions": ["What are the components?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Simulate modes of data flow", "description": "By the end of the sub strand the learner should be able to simulate modes of data flow in communication systems", "learning_experiences": ["Illustrate simplex, half-duplex, full-duplex modes"], "inquiry_questions": ["What are the data flow modes?"], "competencies": ["Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Unity"]}
                ]
            },
            {
                "name": "Data Transmission Media",
                "slos": [
                    {"name": "Define basic concepts in data transmission", "description": "By the end of the sub strand the learner should be able to define basic concepts used in data transmission", "learning_experiences": ["Search for definitions of transmission media, encoding, modulation, multiplexing", "Discuss types of transmission media used in networks", "Draw illustrations of data transmission signals", "Connect digital devices using transmission media", "Share resources through connected devices"], "inquiry_questions": ["What is data transmission?"], "competencies": ["Communication and Collaboration", "Digital Literacy"], "pcis": ["Life Skills"], "values": ["Unity", "Peace"]},
                    {"name": "Describe types of transmission media", "description": "By the end of the sub strand the learner should be able to describe types of transmission media used in computer networks", "learning_experiences": ["Discuss types of transmission media in computer networks"], "inquiry_questions": ["What types of transmission media exist?"], "competencies": ["Communication and Collaboration"], "pcis": ["Life Skills"], "values": ["Peace"]},
                    {"name": "Connect digital devices for data communication", "description": "By the end of the sub strand the learner should be able to connect digital devices used in data communication", "learning_experiences": ["Connect digital devices using transmission media while observing safety"], "inquiry_questions": ["How do we connect devices?"], "competencies": ["Digital Literacy"], "pcis": ["Safety and Security"], "values": ["Responsibility"]},
                    {"name": "Establish factors affecting network communication", "description": "By the end of the sub strand the learner should be able to establish factors that affect communication over a computer network", "learning_experiences": ["Discuss factors that lead to transmission impairment"], "inquiry_questions": ["What affects network communication?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Computer Network Elements",
                "slos": [
                    {"name": "Identify different types of computer networks", "description": "By the end of the sub strand the learner should be able to identify different types of computer networks", "learning_experiences": ["Search for information on LAN, MAN, WAN, PAN, WLAN", "Visit computer user environment to identify network type", "Discuss functions of network devices and software", "Discuss network standards and protocols", "Connect digital device to available network"], "inquiry_questions": ["What types of computer networks exist?"], "competencies": ["Citizenship", "Digital Literacy"], "pcis": ["Citizenship Education"], "values": ["Respect", "Social Justice"]},
                    {"name": "Describe elements of a computer network", "description": "By the end of the sub strand the learner should be able to describe elements of a computer network", "learning_experiences": ["Identify components of network: transmission media, DTE, DCE, network software"], "inquiry_questions": ["What are the elements of a network?"], "competencies": ["Communication and Collaboration"], "pcis": ["Life Skills"], "values": ["Respect"]},
                    {"name": "Evaluate criteria of a computer network", "description": "By the end of the sub strand the learner should be able to evaluate criteria of a computer network", "learning_experiences": ["Discuss network qualities: performance, security, scalability, reliability"], "inquiry_questions": ["What makes a good network?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Connect a computing device to network", "description": "By the end of the sub strand the learner should be able to connect a computing device to available network", "learning_experiences": ["Connect digital device to wired or wireless network and share data"], "inquiry_questions": ["How do we connect to a network?"], "competencies": ["Digital Literacy"], "pcis": ["Safety and Security"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Network Topologies",
                "slos": [
                    {"name": "Differentiate physical and logical topologies", "description": "By the end of the sub strand the learner should be able to differentiate between physical and logical network topologies", "learning_experiences": ["Search for definition of network topology", "Identify differences between physical and logical topologies", "Draw illustrations of star, ring, bus, mesh, tree, hybrid topologies", "Simulate a physical network topology", "Select appropriate topology for given situation"], "inquiry_questions": ["What are the different network topologies?"], "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Unity", "Love"]},
                    {"name": "Describe types of topologies in networking", "description": "By the end of the sub strand the learner should be able to describe types of logical and physical topologies in computer networking", "learning_experiences": ["Draw illustrations of different physical topologies"], "inquiry_questions": ["What are the types of topologies?"], "competencies": ["Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Unity"]},
                    {"name": "Create a physical network topology", "description": "By the end of the sub strand the learner should be able to create a physical network topology for a computer network", "learning_experiences": ["Simulate a physical network topology using available devices"], "inquiry_questions": ["How do we create a network topology?"], "competencies": ["Creativity and Imagination", "Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            }
        ]
    },
    {
        "name": "Software Development",
        "substrands": [
            {
                "name": "Computer Programming Concepts",
                "slos": [
                    {"name": "Explain terminologies in programming languages", "description": "By the end of the sub strand the learner should be able to explain the terminologies used in programming languages", "learning_experiences": ["Discuss terminologies: programming, compiler, interpreter, syntax, source code", "Search for information on evolution of programming languages", "Discuss levels of programming languages: low level and high level", "Search for information about programming paradigms", "Write simple instructions to show machine and assembly language"], "inquiry_questions": ["What are the basic programming concepts?"], "competencies": ["Communication and Collaboration", "Learning to Learn"], "pcis": ["Life Skills"], "values": ["Unity", "Respect"]},
                    {"name": "Describe evolution of programming languages", "description": "By the end of the sub strand the learner should be able to describe evolution of programming languages in software development", "learning_experiences": ["Search for information on evolution of programming languages"], "inquiry_questions": ["How have programming languages evolved?"], "competencies": ["Learning to Learn"], "pcis": ["Life Skills"], "values": ["Respect"]},
                    {"name": "Categorise programming languages by paradigms", "description": "By the end of the sub strand the learner should be able to categorise the programming languages according to the paradigms", "learning_experiences": ["Search for information about structured, procedural, object-oriented paradigms"], "inquiry_questions": ["What are the programming paradigms?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Create instructions to simulate low level languages", "description": "By the end of the sub strand the learner should be able to create simple instructions to simulate low level programming languages", "learning_experiences": ["Write simple instructions to show machine and assembly language"], "inquiry_questions": ["How do low level languages work?"], "competencies": ["Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Program Development",
                "slos": [
                    {"name": "Describe stages of program development", "description": "By the end of the sub strand the learner should be able to describe stages of program development in computer programming", "learning_experiences": ["Discuss stages: problem definition, program design, coding, testing, implementation", "Discuss characteristics of an algorithm: input, output, finite, definite", "Discuss keywords used in pseudocodes: start, variables, input, output", "Draw a flowchart to illustrate logical flow of algorithm", "Use pseudocodes and flowcharts to solve real life problems"], "inquiry_questions": ["What are the stages of program development?"], "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"], "pcis": ["Environmental Education"], "values": ["Unity", "Respect"]},
                    {"name": "Write a pseudocode for an algorithm", "description": "By the end of the sub strand the learner should be able to write a pseudocode to illustrate the logical flow of an algorithm", "learning_experiences": ["Use keywords to write a pseudocode illustrating logical flow"], "inquiry_questions": ["How do we write pseudocode?"], "competencies": ["Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Represent algorithm using a flowchart", "description": "By the end of the sub strand the learner should be able to represent the logical flow of an algorithm using a flowchart", "learning_experiences": ["Draw a flowchart using standard symbols"], "inquiry_questions": ["How do we draw flowcharts?"], "competencies": ["Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Design an algorithm to solve real life problems", "description": "By the end of the sub strand the learner should be able to design an algorithm to solve a real life problem", "learning_experiences": ["Use pseudocodes and flowcharts to solve real life problems"], "inquiry_questions": ["How do we apply algorithms?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Identifiers and Operators",
                "slos": [
                    {"name": "Describe elementary elements of a computer program", "description": "By the end of the sub strand the learner should be able to describe the elementary elements of a computer program", "learning_experiences": ["Discuss structural elements: structure, syntax, errors", "Brainstorm on reserved words, identifiers and data types", "Write computer programs using high-level language", "Watch video on declaration of variables and constants", "Use operators in programs: arithmetic, assignment, relational, logical"], "inquiry_questions": ["What are the elementary programming elements?"], "competencies": ["Creativity and Imagination", "Learning to Learn"], "pcis": ["Citizenship Education"], "values": ["Unity", "Respect"]},
                    {"name": "Declare variables and constants", "description": "By the end of the sub strand the learner should be able to declare variables and constants in a programming language", "learning_experiences": ["Watch video on declaration of variables and constants"], "inquiry_questions": ["How do we declare variables?"], "competencies": ["Digital Literacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Use input and output statements", "description": "By the end of the sub strand the learner should be able to use input and output statements in a programming language", "learning_experiences": ["Write and execute programs that accept input and display output"], "inquiry_questions": ["How do we use I/O statements?"], "competencies": ["Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Use operators in programming", "description": "By the end of the sub strand the learner should be able to use operators in a programming language", "learning_experiences": ["Write and execute programs using arithmetic, assignment, relational operators"], "inquiry_questions": ["How do we use operators?"], "competencies": ["Creativity and Imagination", "Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Control Structures",
                "slos": [
                    {"name": "Describe control structures in programming", "description": "By the end of the sub strand the learner should be able to describe control structures in programming", "learning_experiences": ["Search for information on control structures: sequential, iteration, selection", "Watch video on using decision statements", "Write and execute programs using decision statements", "Write programs with break and continue statements"], "inquiry_questions": ["What are control structures?"], "competencies": ["Critical Thinking and Problem Solving", "Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Respect", "Social Justice"]},
                    {"name": "Select program control structure for situations", "description": "By the end of the sub strand the learner should be able to select program control structure for a given situation", "learning_experiences": ["Identify appropriate control structure for different situations"], "inquiry_questions": ["How do we select control structures?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Use control structures in programming", "description": "By the end of the sub strand the learner should be able to use control structures in programming", "learning_experiences": ["Write and execute programs involving decision statements, break and continue"], "inquiry_questions": ["How do we use control structures?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Data Structures",
                "slos": [
                    {"name": "Describe types of containers in programming", "description": "By the end of the sub strand the learner should be able to describe types of containers in programming", "learning_experiences": ["Brainstorm on data structures: lists, arrays, dictionaries, sets, tuples", "Watch video on declaration of single and two dimensional arrays", "Discuss syntax of data structures in programming", "Write and execute programs using data structures", "Demonstrate sorting and searching techniques"], "inquiry_questions": ["What are data structures?"], "competencies": ["Digital Literacy", "Learning to Learn"], "pcis": ["Citizenship Education"], "values": ["Peace", "Respect"]},
                    {"name": "Use containers in programming", "description": "By the end of the sub strand the learner should be able to use containers in programming", "learning_experiences": ["Write examples of lists, dictionaries, sets, tuples in programming"], "inquiry_questions": ["How do we use containers?"], "competencies": ["Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Apply sorting and searching techniques", "description": "By the end of the sub strand the learner should be able to apply sorting and searching techniques in data structures", "learning_experiences": ["Demonstrate sequential search, binary search, and sorting algorithms"], "inquiry_questions": ["How do we sort and search data?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Functions",
                "slos": [
                    {"name": "Discuss types of functions in modular programming", "description": "By the end of the sub strand the learner should be able to discuss types of function used in modular programming", "learning_experiences": ["Search for meaning and importance of modular programming", "Discuss differences between user defined and built-in functions", "Discuss general syntax of a function", "Search for information on parameter passing", "Write and execute programs using built-in and user-defined functions"], "inquiry_questions": ["What are functions in programming?"], "competencies": ["Self-Efficacy", "Digital Literacy"], "pcis": ["Life Skills"], "values": ["Unity", "Peace"]},
                    {"name": "Use built-in and user-defined functions", "description": "By the end of the sub strand the learner should be able to use built-in and user-defined functions to create a modular program", "learning_experiences": ["Write and execute programs using built-in and user-defined functions"], "inquiry_questions": ["How do we use functions?"], "competencies": ["Self-Efficacy", "Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Discuss scope of variables and parameter passing", "description": "By the end of the sub strand the learner should be able to discuss the scope of variables and parameter passing between functions", "learning_experiences": ["Discuss and present scope of local and global variables"], "inquiry_questions": ["What is variable scope?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            }
        ]
    }
]

# FASIHI YA KISWAHILI - Grade 10 (abbreviated for space - will follow similar pattern)
FASIHI_YA_KISWAHILI_STRANDS = [
    {
        "name": "Fasihi Simulizi",
        "substrands": [
            {
                "name": "Utangulizi wa Fasihi Simulizi",
                "slos": [
                    {"name": "Kueleza dhana ya fasihi simulizi", "description": "Kueleza dhana ya fasihi simulizi na sifa zake", "learning_experiences": ["Kutumia vifaa vya kidijitali kutafuta habari kuhusu fasihi simulizi", "Kujadili sifa za fasihi simulizi"], "inquiry_questions": ["Fasihi simulizi ni nini?"], "competencies": ["Communication and Collaboration", "Digital Literacy"], "pcis": ["Citizenship Education"], "values": ["Unity", "Respect"]},
                    {"name": "Kubainisha aina za fasihi simulizi", "description": "Kubainisha aina za fasihi simulizi", "learning_experiences": ["Kujadili aina mbalimbali za fasihi simulizi"], "inquiry_questions": ["Kuna aina gani za fasihi simulizi?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            },
            {
                "name": "Hadithi",
                "slos": [
                    {"name": "Kueleza aina za hadithi", "description": "Kueleza aina za hadithi za fasihi simulizi", "learning_experiences": ["Kujadili hekaya, hurafa, ngano za mazimwi na mighani", "Kusimulia hadithi mbalimbali"], "inquiry_questions": ["Hadithi ni nini?"], "competencies": ["Communication and Collaboration", "Creativity and Imagination"], "pcis": ["Life Skills", "Citizenship Education"], "values": ["Unity", "Love"]},
                    {"name": "Kusimulia hadithi", "description": "Kusimulia hadithi za aina mbalimbali", "learning_experiences": ["Kusimulia hekaya, hurafa na ngano"], "inquiry_questions": ["Tunasimulije hadithi?"], "competencies": ["Communication and Collaboration"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            },
            {
                "name": "Semi",
                "slos": [
                    {"name": "Kueleza dhana ya semi", "description": "Kueleza dhana ya semi na aina zake", "learning_experiences": ["Kujadili methali, misemo, mafumbo na vitendawili", "Kutumia semi katika mazungumzo"], "inquiry_questions": ["Semi ni nini?"], "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"], "pcis": ["Life Skills", "Citizenship Education"], "values": ["Unity", "Respect"]},
                    {"name": "Kutumia semi katika mazungumzo", "description": "Kutumia semi katika mazungumzo ya kila siku", "learning_experiences": ["Kuandika na kutumia methali na misemo"], "inquiry_questions": ["Tunatumije semi?"], "competencies": ["Communication and Collaboration"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            },
            {
                "name": "Nyimbo",
                "slos": [
                    {"name": "Kueleza dhana ya nyimbo", "description": "Kueleza dhana ya nyimbo za fasihi simulizi", "learning_experiences": ["Kujadili aina za nyimbo", "Kuimba nyimbo mbalimbali"], "inquiry_questions": ["Nyimbo ni nini?"], "competencies": ["Creativity and Imagination", "Communication and Collaboration"], "pcis": ["Citizenship Education", "Life Skills"], "values": ["Unity", "Peace"]},
                    {"name": "Kuimba na kuchambua nyimbo", "description": "Kuimba na kuchambua nyimbo mbalimbali", "learning_experiences": ["Kuimba na kuchambua nyimbo za jadi"], "inquiry_questions": ["Tunachambuje nyimbo?"], "competencies": ["Creativity and Imagination"], "pcis": ["Life Skills"], "values": ["Unity"]}
                ]
            }
        ]
    },
    {
        "name": "Ushairi",
        "substrands": [
            {
                "name": "Utangulizi wa Ushairi",
                "slos": [
                    {"name": "Kueleza dhana ya ushairi", "description": "Kueleza dhana ya ushairi na sifa zake", "learning_experiences": ["Kutumia vifaa vya kidijitali kutafuta habari kuhusu ushairi", "Kujadili sifa za ushairi"], "inquiry_questions": ["Ushairi ni nini?"], "competencies": ["Communication and Collaboration", "Digital Literacy"], "pcis": ["Citizenship Education"], "values": ["Unity", "Respect"]},
                    {"name": "Kubainisha sifa za ushairi", "description": "Kubainisha sifa za ushairi wa Kiswahili", "learning_experiences": ["Kujadili vipengele vya ushairi"], "inquiry_questions": ["Ushairi una sifa gani?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            },
            {
                "name": "Aina za Mashairi",
                "slos": [
                    {"name": "Kubainisha aina za mashairi", "description": "Kubainisha aina za mashairi ya Kiswahili", "learning_experiences": ["Kujadili mashairi ya kimapokeo na ya kisasa", "Kusoma na kuchambua mashairi"], "inquiry_questions": ["Kuna aina gani za mashairi?"], "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"], "pcis": ["Life Skills", "Citizenship Education"], "values": ["Unity", "Respect"]},
                    {"name": "Kuchambua mashairi", "description": "Kuchambua mashairi kwa kuzingatia vipengele vyake", "learning_experiences": ["Kuchambua dhamira, mtindo na lugha ya mashairi"], "inquiry_questions": ["Tunachambuaje mashairi?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            }
        ]
    },
    {
        "name": "Bunilizi",
        "substrands": [
            {
                "name": "Riwaya",
                "slos": [
                    {"name": "Kueleza dhana ya riwaya", "description": "Kueleza dhana ya riwaya na sifa zake", "learning_experiences": ["Kusoma riwaya teule", "Kuchambua vipengele vya riwaya"], "inquiry_questions": ["Riwaya ni nini?"], "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"], "pcis": ["Life Skills", "Citizenship Education"], "values": ["Unity", "Respect"]},
                    {"name": "Kuchambua riwaya", "description": "Kuchambua riwaya kwa kuzingatia vipengele vyake", "learning_experiences": ["Kuchambua wahusika, dhamira, mtindo na muundo"], "inquiry_questions": ["Tunachambuaje riwaya?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            },
            {
                "name": "Tamthilia",
                "slos": [
                    {"name": "Kueleza dhana ya tamthilia", "description": "Kueleza dhana ya tamthilia na sifa zake", "learning_experiences": ["Kusoma tamthilia teule", "Kuigiza sehemu za tamthilia"], "inquiry_questions": ["Tamthilia ni nini?"], "competencies": ["Communication and Collaboration", "Creativity and Imagination"], "pcis": ["Life Skills", "Citizenship Education"], "values": ["Unity", "Respect"]},
                    {"name": "Kuchambua tamthilia", "description": "Kuchambua tamthilia kwa kuzingatia vipengele vyake", "learning_experiences": ["Kuchambua wahusika, dhamira, mandhari na mbinu za uigizaji"], "inquiry_questions": ["Tunachambuaje tamthilia?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            }
        ]
    }
]

# HISTORY AND CITIZENSHIP - Grade 10
HISTORY_AND_CITIZENSHIP_STRANDS = [
    {
        "name": "Themes in Kenyan History and Citizenship",
        "substrands": [
            {
                "name": "Linguistic Groups in Kenya",
                "slos": [
                    {"name": "Identify linguistic groups in Kenya", "description": "By the end of the sub strand the learner should be able to identify the main linguistic groups in Kenya", "learning_experiences": ["Research on linguistic groups: Bantu, Nilotes, Cushites", "Discuss migration and settlement patterns", "Map the distribution of linguistic groups"], "inquiry_questions": ["What are the main linguistic groups in Kenya?"], "competencies": ["Communication and Collaboration", "Digital Literacy"], "pcis": ["Citizenship Education"], "values": ["Unity", "Respect"]},
                    {"name": "Describe migration and settlement patterns", "description": "By the end of the sub strand the learner should be able to describe the migration and settlement patterns of linguistic groups", "learning_experiences": ["Trace migration routes of various groups"], "inquiry_questions": ["How did different groups migrate?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            },
            {
                "name": "Establishment of Colonial Rule in Kenya",
                "slos": [
                    {"name": "Explain factors that led to colonial rule", "description": "By the end of the sub strand the learner should be able to explain factors that led to establishment of colonial rule in Kenya", "learning_experiences": ["Research on factors: economic, political, social", "Discuss methods used to establish colonial rule", "Analyze impact of colonial rule"], "inquiry_questions": ["What factors led to colonialism?"], "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"], "pcis": ["Citizenship Education"], "values": ["Patriotism", "Unity"]},
                    {"name": "Describe methods of colonial administration", "description": "By the end of the sub strand the learner should be able to describe methods of colonial administration", "learning_experiences": ["Discuss direct and indirect rule"], "inquiry_questions": ["How did colonial administration work?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Justice"]}
                ]
            },
            {
                "name": "The Constitution of Kenya 2010",
                "slos": [
                    {"name": "Explain key features of the Constitution", "description": "By the end of the sub strand the learner should be able to explain key features of the Constitution of Kenya 2010", "learning_experiences": ["Study the structure of the Constitution", "Discuss Bill of Rights", "Analyze devolved government structure"], "inquiry_questions": ["What are the key features of our Constitution?"], "competencies": ["Critical Thinking and Problem Solving", "Citizenship"], "pcis": ["Citizenship Education"], "values": ["Patriotism", "Responsibility"]},
                    {"name": "Describe the Bill of Rights", "description": "By the end of the sub strand the learner should be able to describe the Bill of Rights in the Constitution", "learning_experiences": ["Discuss fundamental rights and freedoms"], "inquiry_questions": ["What rights do citizens have?"], "competencies": ["Citizenship"], "pcis": ["Citizenship Education"], "values": ["Justice", "Responsibility"]}
                ]
            },
            {
                "name": "Political Developments Since Independence",
                "slos": [
                    {"name": "Trace political developments since independence", "description": "By the end of the sub strand the learner should be able to trace political developments in Kenya since independence", "learning_experiences": ["Research on single-party era", "Discuss multi-party democracy", "Analyze political reforms"], "inquiry_questions": ["How has Kenya's politics evolved?"], "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"], "pcis": ["Citizenship Education"], "values": ["Patriotism", "Unity"]},
                    {"name": "Explain the transition to multi-party democracy", "description": "By the end of the sub strand the learner should be able to explain the transition to multi-party democracy", "learning_experiences": ["Discuss factors that led to multi-party democracy"], "inquiry_questions": ["Why did Kenya adopt multi-party democracy?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Justice"]}
                ]
            },
            {
                "name": "Elections and National Integration",
                "slos": [
                    {"name": "Explain the electoral process in Kenya", "description": "By the end of the sub strand the learner should be able to explain the electoral process in Kenya", "learning_experiences": ["Study the roles of IEBC", "Discuss types of elections", "Analyze factors promoting national unity"], "inquiry_questions": ["How do elections work in Kenya?"], "competencies": ["Citizenship", "Critical Thinking and Problem Solving"], "pcis": ["Citizenship Education"], "values": ["Patriotism", "Unity"]},
                    {"name": "Discuss factors promoting national integration", "description": "By the end of the sub strand the learner should be able to discuss factors promoting national integration", "learning_experiences": ["Discuss national symbols, holidays, and policies"], "inquiry_questions": ["What promotes national unity?"], "competencies": ["Citizenship"], "pcis": ["Citizenship Education"], "values": ["Unity", "Peace"]}
                ]
            }
        ]
    },
    {
        "name": "Themes in African History and Citizenship",
        "substrands": [
            {
                "name": "Human Developments in Africa",
                "slos": [
                    {"name": "Trace human developments in Africa", "description": "By the end of the sub strand the learner should be able to trace human developments in Africa", "learning_experiences": ["Research on early human evolution in Africa", "Discuss archaeological evidence", "Study cultural developments"], "inquiry_questions": ["What is Africa's role in human evolution?"], "competencies": ["Critical Thinking and Problem Solving", "Digital Literacy"], "pcis": ["Citizenship Education"], "values": ["Patriotism", "Respect"]},
                    {"name": "Explain significance of archaeological sites", "description": "By the end of the sub strand the learner should be able to explain significance of archaeological sites in Africa", "learning_experiences": ["Study sites like Olduvai Gorge, Koobi Fora"], "inquiry_questions": ["Why are these sites important?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Environmental Education"], "values": ["Respect"]}
                ]
            },
            {
                "name": "African Civilizations",
                "slos": [
                    {"name": "Describe ancient African civilizations", "description": "By the end of the sub strand the learner should be able to describe ancient African civilizations up to 19th century", "learning_experiences": ["Research on Egypt, Ghana, Mali, Songhai, Zimbabwe", "Discuss achievements of African kingdoms", "Analyze trade and cultural exchanges"], "inquiry_questions": ["What were the great African civilizations?"], "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"], "pcis": ["Citizenship Education"], "values": ["Patriotism", "Unity"]},
                    {"name": "Analyze achievements of African kingdoms", "description": "By the end of the sub strand the learner should be able to analyze achievements of African kingdoms", "learning_experiences": ["Discuss architecture, trade, governance systems"], "inquiry_questions": ["What did African kingdoms achieve?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Respect"]}
                ]
            },
            {
                "name": "Colonization of Africa",
                "slos": [
                    {"name": "Explain factors that led to colonization of Africa", "description": "By the end of the sub strand the learner should be able to explain factors that led to colonization of Africa", "learning_experiences": ["Study the Berlin Conference", "Discuss scramble and partition of Africa", "Analyze effects of colonialism"], "inquiry_questions": ["Why was Africa colonized?"], "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"], "pcis": ["Citizenship Education"], "values": ["Justice", "Unity"]},
                    {"name": "Describe the scramble and partition of Africa", "description": "By the end of the sub strand the learner should be able to describe the scramble and partition of Africa", "learning_experiences": ["Study maps showing colonial boundaries"], "inquiry_questions": ["How was Africa partitioned?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Justice"]}
                ]
            },
            {
                "name": "Modern Nationalism in Africa",
                "slos": [
                    {"name": "Trace the rise of nationalism in Africa", "description": "By the end of the sub strand the learner should be able to trace the rise of nationalism in Africa", "learning_experiences": ["Research on Pan-Africanism", "Study independence movements", "Discuss role of African leaders"], "inquiry_questions": ["How did African nationalism arise?"], "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"], "pcis": ["Citizenship Education"], "values": ["Patriotism", "Unity"]},
                    {"name": "Explain role of Pan-Africanism", "description": "By the end of the sub strand the learner should be able to explain the role of Pan-Africanism in independence", "learning_experiences": ["Discuss Pan-African congresses and leaders"], "inquiry_questions": ["What is Pan-Africanism?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Citizenship Education"], "values": ["Unity"]}
                ]
            }
        ]
    },
    {
        "name": "International Themes in History and Citizenship",
        "substrands": [
            {
                "name": "Great Revolutions",
                "slos": [
                    {"name": "Explain causes and effects of revolutions", "description": "By the end of the sub strand the learner should be able to explain causes and effects of great revolutions", "learning_experiences": ["Study the French Revolution", "Analyze causes: political, economic, social", "Discuss impact on world history"], "inquiry_questions": ["What caused the great revolutions?"], "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"], "pcis": ["Citizenship Education"], "values": ["Justice", "Responsibility"]},
                    {"name": "Analyze the French Revolution", "description": "By the end of the sub strand the learner should be able to analyze the French Revolution and its impact", "learning_experiences": ["Study events and outcomes of the French Revolution"], "inquiry_questions": ["What was the French Revolution?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Justice"]}
                ]
            },
            {
                "name": "International Organizations",
                "slos": [
                    {"name": "Describe major international organizations", "description": "By the end of the sub strand the learner should be able to describe major international organizations", "learning_experiences": ["Research on UN, AU, EAC", "Discuss roles and functions", "Analyze Kenya's participation"], "inquiry_questions": ["What are international organizations?"], "competencies": ["Citizenship", "Communication and Collaboration"], "pcis": ["Citizenship Education"], "values": ["Peace", "Unity"]},
                    {"name": "Explain Kenya's role in international bodies", "description": "By the end of the sub strand the learner should be able to explain Kenya's role in international bodies", "learning_experiences": ["Discuss Kenya's participation in UN, AU"], "inquiry_questions": ["What is Kenya's international role?"], "competencies": ["Citizenship"], "pcis": ["Citizenship Education"], "values": ["Patriotism"]}
                ]
            },
            {
                "name": "Global Governance",
                "slos": [
                    {"name": "Explain concepts of global governance", "description": "By the end of the sub strand the learner should be able to explain concepts of global governance", "learning_experiences": ["Discuss global issues: climate change, trade, security", "Analyze role of international law", "Study cooperation between nations"], "inquiry_questions": ["What is global governance?"], "competencies": ["Citizenship", "Critical Thinking and Problem Solving"], "pcis": ["Environmental Education", "Citizenship Education"], "values": ["Peace", "Responsibility"]},
                    {"name": "Analyze global challenges and responses", "description": "By the end of the sub strand the learner should be able to analyze global challenges and responses", "learning_experiences": ["Study responses to climate change, terrorism, pandemics"], "inquiry_questions": ["How does the world address challenges?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Environmental Education"], "values": ["Responsibility"]}
                ]
            }
        ]
    },
    {
        "name": "Contemporary Themes in History and Citizenship",
        "substrands": [
            {
                "name": "Peace and Conflict Transformation",
                "slos": [
                    {"name": "Explain concepts of peace and conflict", "description": "By the end of the sub strand the learner should be able to explain concepts of peace and conflict transformation", "learning_experiences": ["Discuss causes of conflict", "Study peace building mechanisms", "Analyze Kenya's experience with conflict"], "inquiry_questions": ["What causes conflict and how is peace built?"], "competencies": ["Critical Thinking and Problem Solving", "Citizenship"], "pcis": ["Life Skills", "Citizenship Education"], "values": ["Peace", "Unity"]},
                    {"name": "Discuss peace building mechanisms", "description": "By the end of the sub strand the learner should be able to discuss peace building mechanisms in Kenya", "learning_experiences": ["Study mediation, truth commissions, reconciliation"], "inquiry_questions": ["How do we build peace?"], "competencies": ["Citizenship"], "pcis": ["Life Skills"], "values": ["Peace"]}
                ]
            },
            {
                "name": "The 4th Industrial Revolution",
                "slos": [
                    {"name": "Explain the 4th Industrial Revolution", "description": "By the end of the sub strand the learner should be able to explain the 4th Industrial Revolution and its technologies", "learning_experiences": ["Research on AI, IoT, robotics, blockchain", "Discuss impact on society and economy", "Analyze opportunities and challenges"], "inquiry_questions": ["What is the 4th Industrial Revolution?"], "competencies": ["Digital Literacy", "Critical Thinking and Problem Solving"], "pcis": ["Life Skills", "Environmental Education"], "values": ["Responsibility", "Integrity"]},
                    {"name": "Analyze impact of emerging technologies", "description": "By the end of the sub strand the learner should be able to analyze impact of emerging technologies on society", "learning_experiences": ["Discuss changes in work, education, and daily life"], "inquiry_questions": ["How do technologies change society?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Equity and Non-Discrimination",
                "slos": [
                    {"name": "Explain concepts of equity and non-discrimination", "description": "By the end of the sub strand the learner should be able to explain concepts of equity and non-discrimination", "learning_experiences": ["Discuss human rights principles", "Study anti-discrimination laws in Kenya", "Analyze gender equality and inclusion"], "inquiry_questions": ["What is equity and non-discrimination?"], "competencies": ["Citizenship", "Critical Thinking and Problem Solving"], "pcis": ["Citizenship Education", "Life Skills"], "values": ["Justice", "Respect"]},
                    {"name": "Discuss measures to promote equity", "description": "By the end of the sub strand the learner should be able to discuss measures to promote equity in Kenya", "learning_experiences": ["Study affirmative action, equal opportunity policies"], "inquiry_questions": ["How do we promote equity?"], "competencies": ["Citizenship"], "pcis": ["Citizenship Education"], "values": ["Justice"]}
                ]
            }
        ]
    }
]

# HOME SCIENCE - Grade 10
HOME_SCIENCE_STRANDS = [
    {
        "name": "Foods and Nutrition",
        "substrands": [
            {
                "name": "Introduction to Foods and Nutrition",
                "slos": [
                    {"name": "Explain importance of food and nutrition", "description": "By the end of the sub strand the learner should be able to explain the importance of food and nutrition", "learning_experiences": ["Discuss functions of food in the body", "Research on nutrients and their sources", "Identify nutritional needs at different life stages"], "inquiry_questions": ["Why is food and nutrition important?"], "competencies": ["Communication and Collaboration", "Digital Literacy"], "pcis": ["Health Education"], "values": ["Responsibility", "Love"]},
                    {"name": "Identify nutrients and their sources", "description": "By the end of the sub strand the learner should be able to identify nutrients and their sources", "learning_experiences": ["Research on proteins, carbohydrates, fats, vitamins, minerals"], "inquiry_questions": ["What nutrients do we need?"], "competencies": ["Digital Literacy"], "pcis": ["Health Education"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Meal Planning",
                "slos": [
                    {"name": "Explain principles of meal planning", "description": "By the end of the sub strand the learner should be able to explain principles of meal planning", "learning_experiences": ["Discuss factors to consider in meal planning", "Plan balanced meals for different occasions", "Consider nutritional needs of different groups"], "inquiry_questions": ["How do we plan meals?"], "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"], "pcis": ["Health Education", "Financial Literacy"], "values": ["Responsibility", "Love"]},
                    {"name": "Plan balanced meals", "description": "By the end of the sub strand the learner should be able to plan balanced meals for different occasions", "learning_experiences": ["Create meal plans considering nutritional balance"], "inquiry_questions": ["What makes a balanced meal?"], "competencies": ["Creativity and Imagination"], "pcis": ["Health Education"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Cooking Methods",
                "slos": [
                    {"name": "Describe different cooking methods", "description": "By the end of the sub strand the learner should be able to describe different cooking methods", "learning_experiences": ["Demonstrate boiling, steaming, frying, baking, roasting", "Discuss effects of cooking on nutrients", "Practice safe food handling"], "inquiry_questions": ["What are the different cooking methods?"], "competencies": ["Self-Efficacy", "Creativity and Imagination"], "pcis": ["Health Education", "Safety and Security"], "values": ["Responsibility", "Integrity"]},
                    {"name": "Apply cooking methods in food preparation", "description": "By the end of the sub strand the learner should be able to apply cooking methods in food preparation", "learning_experiences": ["Prepare foods using different cooking methods"], "inquiry_questions": ["How do we apply cooking methods?"], "competencies": ["Self-Efficacy"], "pcis": ["Health Education"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Food Hygiene and Safety",
                "slos": [
                    {"name": "Explain principles of food hygiene and safety", "description": "By the end of the sub strand the learner should be able to explain principles of food hygiene and safety", "learning_experiences": ["Discuss personal and kitchen hygiene", "Identify causes of food contamination", "Practice safe food storage methods"], "inquiry_questions": ["Why is food hygiene important?"], "competencies": ["Critical Thinking and Problem Solving", "Self-Efficacy"], "pcis": ["Health Education", "Safety and Security"], "values": ["Responsibility", "Integrity"]},
                    {"name": "Apply food safety practices", "description": "By the end of the sub strand the learner should be able to apply food safety practices", "learning_experiences": ["Demonstrate safe food handling and storage"], "inquiry_questions": ["How do we keep food safe?"], "competencies": ["Self-Efficacy"], "pcis": ["Safety and Security"], "values": ["Responsibility"]}
                ]
            }
        ]
    },
    {
        "name": "Home Management",
        "substrands": [
            {
                "name": "Hygiene During Puberty",
                "slos": [
                    {"name": "Explain changes during puberty", "description": "By the end of the sub strand the learner should be able to explain changes during puberty", "learning_experiences": ["Discuss physical and emotional changes", "Learn about personal hygiene practices", "Discuss menstrual hygiene management"], "inquiry_questions": ["What changes occur during puberty?"], "competencies": ["Communication and Collaboration", "Self-Efficacy"], "pcis": ["Health Education", "Life Skills"], "values": ["Respect", "Responsibility"]},
                    {"name": "Practice personal hygiene during puberty", "description": "By the end of the sub strand the learner should be able to practice personal hygiene during puberty", "learning_experiences": ["Demonstrate hygiene practices for adolescents"], "inquiry_questions": ["How do we maintain hygiene during puberty?"], "competencies": ["Self-Efficacy"], "pcis": ["Health Education"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Home Safety and First Aid",
                "slos": [
                    {"name": "Identify home safety hazards", "description": "By the end of the sub strand the learner should be able to identify home safety hazards", "learning_experiences": ["Discuss common home accidents", "Learn fire safety measures", "Practice basic first aid procedures"], "inquiry_questions": ["What are home safety hazards?"], "competencies": ["Critical Thinking and Problem Solving", "Self-Efficacy"], "pcis": ["Safety and Security", "Health Education"], "values": ["Responsibility", "Love"]},
                    {"name": "Apply first aid procedures", "description": "By the end of the sub strand the learner should be able to apply basic first aid procedures", "learning_experiences": ["Demonstrate first aid for cuts, burns, choking"], "inquiry_questions": ["How do we give first aid?"], "competencies": ["Self-Efficacy"], "pcis": ["Health Education"], "values": ["Love"]}
                ]
            },
            {
                "name": "Housing the Family",
                "slos": [
                    {"name": "Explain factors in selecting a house", "description": "By the end of the sub strand the learner should be able to explain factors to consider in selecting a house", "learning_experiences": ["Discuss housing needs for families", "Consider location, size, cost, facilities", "Learn about home arrangement and furnishing"], "inquiry_questions": ["What factors affect housing choice?"], "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"], "pcis": ["Financial Literacy", "Environmental Education"], "values": ["Responsibility", "Peace"]},
                    {"name": "Arrange and furnish living spaces", "description": "By the end of the sub strand the learner should be able to arrange and furnish living spaces", "learning_experiences": ["Practice arranging furniture and decorating"], "inquiry_questions": ["How do we arrange living spaces?"], "competencies": ["Creativity and Imagination"], "pcis": ["Environmental Education"], "values": ["Peace"]}
                ]
            },
            {
                "name": "Cleaning Practices",
                "slos": [
                    {"name": "Describe cleaning equipment and materials", "description": "By the end of the sub strand the learner should be able to describe cleaning equipment and materials", "learning_experiences": ["Identify cleaning tools and agents", "Discuss cleaning different surfaces", "Practice cleaning routines"], "inquiry_questions": ["What equipment do we need for cleaning?"], "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"], "pcis": ["Environmental Education", "Health Education"], "values": ["Responsibility", "Integrity"]},
                    {"name": "Apply cleaning techniques", "description": "By the end of the sub strand the learner should be able to apply cleaning techniques for different surfaces", "learning_experiences": ["Clean various surfaces using appropriate methods"], "inquiry_questions": ["How do we clean different surfaces?"], "competencies": ["Self-Efficacy"], "pcis": ["Health Education"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Consumer Education",
                "slos": [
                    {"name": "Explain consumer rights and responsibilities", "description": "By the end of the sub strand the learner should be able to explain consumer rights and responsibilities", "learning_experiences": ["Discuss consumer protection laws", "Learn about budgeting and wise spending", "Practice comparison shopping"], "inquiry_questions": ["What are consumer rights?"], "competencies": ["Critical Thinking and Problem Solving", "Citizenship"], "pcis": ["Financial Literacy", "Citizenship Education"], "values": ["Integrity", "Responsibility"]},
                    {"name": "Practice wise consumer behavior", "description": "By the end of the sub strand the learner should be able to practice wise consumer behavior", "learning_experiences": ["Create budgets and compare products"], "inquiry_questions": ["How do we make wise purchases?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Financial Literacy"], "values": ["Integrity"]}
                ]
            }
        ]
    },
    {
        "name": "Clothing and Textiles",
        "substrands": [
            {
                "name": "Sewing Tools and Equipment",
                "slos": [
                    {"name": "Identify sewing tools and equipment", "description": "By the end of the sub strand the learner should be able to identify sewing tools and equipment", "learning_experiences": ["Discuss different sewing tools and their uses", "Practice safe handling of sewing equipment", "Learn to use a sewing machine"], "inquiry_questions": ["What tools do we need for sewing?"], "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"], "pcis": ["Safety and Security", "Life Skills"], "values": ["Responsibility", "Integrity"]},
                    {"name": "Use sewing tools safely", "description": "By the end of the sub strand the learner should be able to use sewing tools safely", "learning_experiences": ["Demonstrate safe handling and use of sewing tools"], "inquiry_questions": ["How do we use sewing tools safely?"], "competencies": ["Self-Efficacy"], "pcis": ["Safety and Security"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Textile Fibres",
                "slos": [
                    {"name": "Classify textile fibres", "description": "By the end of the sub strand the learner should be able to classify textile fibres", "learning_experiences": ["Discuss natural and synthetic fibres", "Identify properties of different fibres", "Practice fabric identification tests"], "inquiry_questions": ["What are the different types of fibres?"], "competencies": ["Critical Thinking and Problem Solving", "Digital Literacy"], "pcis": ["Environmental Education", "Life Skills"], "values": ["Responsibility", "Respect"]},
                    {"name": "Identify properties of textile fibres", "description": "By the end of the sub strand the learner should be able to identify properties of textile fibres", "learning_experiences": ["Test and identify different fabric types"], "inquiry_questions": ["What are the properties of fibres?"], "competencies": ["Critical Thinking and Problem Solving"], "pcis": ["Environmental Education"], "values": ["Responsibility"]}
                ]
            },
            {
                "name": "Clothing Construction",
                "slos": [
                    {"name": "Describe clothing construction processes", "description": "By the end of the sub strand the learner should be able to describe clothing construction processes", "learning_experiences": ["Learn different types of stitches", "Practice making seams and hems", "Construct simple garments"], "inquiry_questions": ["How do we construct clothing?"], "competencies": ["Self-Efficacy", "Creativity and Imagination"], "pcis": ["Life Skills", "Financial Literacy"], "values": ["Responsibility", "Integrity"]},
                    {"name": "Apply stitches and seams in construction", "description": "By the end of the sub strand the learner should be able to apply stitches and seams in clothing construction", "learning_experiences": ["Practice temporary and permanent stitches, seams"], "inquiry_questions": ["How do we use stitches and seams?"], "competencies": ["Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]},
                    {"name": "Construct simple garments", "description": "By the end of the sub strand the learner should be able to construct simple garments", "learning_experiences": ["Make simple articles like cushion covers, bags, aprons"], "inquiry_questions": ["How do we make simple garments?"], "competencies": ["Creativity and Imagination", "Self-Efficacy"], "pcis": ["Life Skills"], "values": ["Responsibility"]}
                ]
            }
        ]
    }
]

async def main():
    """Main function to seed all Grade 10 subjects"""
    print("="*80)
    print("GRADE 10 CURRICULUM SEEDING")
    print("="*80)
    
    # Get or create Grade 10
    grade10 = await db.grades.find_one({'name': 'Grade 10'})
    if not grade10:
        result = await db.grades.insert_one({'name': 'Grade 10', 'order': 10})
        grade10_id = result.inserted_id
        print(f"Created Grade 10 with ID: {grade10_id}")
    else:
        grade10_id = grade10['_id']
        print(f"Found Grade 10 with ID: {grade10_id}")
    
    # Get reference IDs
    comp_map, val_map, pci_map = await get_reference_ids()
    print(f"Loaded {len(comp_map)} competencies, {len(val_map)} values, {len(pci_map)} PCIs")
    
    # Seed all subjects
    subjects_data = [
        ("Agriculture", AGRICULTURE_STRANDS),
        ("Computer Science", COMPUTER_SCIENCE_STRANDS),
        ("Fasihi ya Kiswahili", FASIHI_YA_KISWAHILI_STRANDS),
        ("History and Citizenship", HISTORY_AND_CITIZENSHIP_STRANDS),
        ("Home Science", HOME_SCIENCE_STRANDS)
    ]
    
    total_stats = {"strands": 0, "substrands": 0, "slos": 0, "mappings": 0}
    
    for subject_name, strands_data in subjects_data:
        strands, substrands, slos, mappings = await seed_subject(
            subject_name, strands_data, grade10_id, comp_map, val_map, pci_map
        )
        total_stats["strands"] += strands
        total_stats["substrands"] += substrands
        total_stats["slos"] += slos
        total_stats["mappings"] += mappings
    
    print("\n" + "="*80)
    print("SEEDING COMPLETE - SUMMARY")
    print("="*80)
    print(f"Total Strands: {total_stats['strands']}")
    print(f"Total Substrands: {total_stats['substrands']}")
    print(f"Total SLOs: {total_stats['slos']}")
    print(f"Total SLO Mappings: {total_stats['mappings']}")

if __name__ == "__main__":
    asyncio.run(main())
