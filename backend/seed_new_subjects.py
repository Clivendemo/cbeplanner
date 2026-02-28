#!/usr/bin/env python3
"""
Seed curriculum data for 5 new subjects from KICD PDFs:
- Business Studies
- Christian Religious Education (CRE)
- Electrical Technology
- Fine Arts
- French

Run with: python seed_new_subjects.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# ============================================================================
# BUSINESS STUDIES
# ============================================================================
BUSINESS_STUDIES_DATA = {
    "strands": [
        {
            "name": "Business and Money Management",
            "substrands": [
                {
                    "name": "Money",
                    "slos": [
                        {"name": "Identify the key security features of Kenyan currency", "description": "By the end of the lesson, the learner should be able to identify the key security features of the Kenyan currency."},
                        {"name": "Describe the functions of money in financial transactions", "description": "By the end of the lesson, the learner should be able to describe the functions of money when carrying out financial transactions."},
                        {"name": "Justify the demand for money for economic development", "description": "By the end of the lesson, the learner should be able to justify the demand for money for achieving economic development."},
                        {"name": "Examine factors determining supply of money", "description": "By the end of the lesson, the learner should be able to examine the factors that determine supply of money in an economy."},
                        {"name": "Evaluate ethical practices on use of money", "description": "By the end of the lesson, the learner should be able to evaluate ethical practices on the use of money in financial transactions."},
                        {"name": "Acknowledge the role of money in daily life", "description": "By the end of the lesson, the learner should be able to acknowledge the role of money in day-to-day life."}
                    ]
                },
                {
                    "name": "Business Goals",
                    "slos": [
                        {"name": "Analyse the importance of goal setting in business", "description": "By the end of the lesson, the learner should be able to analyse the importance of goal setting in business."},
                        {"name": "Examine factors to consider when setting business goals", "description": "By the end of the lesson, the learner should be able to examine the factors to consider when setting goals for a business."},
                        {"name": "Describe steps for setting business goals", "description": "By the end of the lesson, the learner should be able to describe steps followed when setting business goals."},
                        {"name": "Formulate SMART business goals", "description": "By the end of the lesson, the learner should be able to formulate SMART short term and long term goals for a business."},
                        {"name": "Appreciate the need for setting goals", "description": "By the end of the lesson, the learner should be able to appreciate the need for setting goals in business."}
                    ]
                },
                {
                    "name": "Budgeting in Business",
                    "slos": [
                        {"name": "Explain the importance of budgeting", "description": "By the end of the lesson, the learner should be able to explain the importance of budgeting in business."},
                        {"name": "Analyse types of business budgets", "description": "By the end of the lesson, the learner should be able to analyse the types of business budgets for financial planning."},
                        {"name": "Prepare a budget to control spending", "description": "By the end of the lesson, the learner should be able to prepare a budget to control spending in business."},
                        {"name": "Appreciate the need for budgeting", "description": "By the end of the lesson, the learner should be able to appreciate the need for budgeting in business."}
                    ]
                },
                {
                    "name": "Banking",
                    "slos": [
                        {"name": "Explain the importance of banking in an economy", "description": "By the end of the lesson, the learner should be able to explain the importance of banking in an economy."},
                        {"name": "Analyse types of accounts offered by banks", "description": "By the end of the lesson, the learner should be able to analyse types of accounts offered by banks."},
                        {"name": "Explore ethical practices in banking", "description": "By the end of the lesson, the learner should be able to explore the ethical practices in banking."},
                        {"name": "Describe trends in banking in Kenya", "description": "By the end of the lesson, the learner should be able to describe the trends in banking in Kenya."},
                        {"name": "Appreciate the role of banking in the economy", "description": "By the end of the lesson, the learner should be able to appreciate the role of banking in an economy."}
                    ]
                }
            ]
        },
        {
            "name": "Business and Its Environment",
            "substrands": [
                {
                    "name": "Business Activities",
                    "slos": [
                        {"name": "Explain the concept of needs and wants", "description": "By the end of the lesson, the learner should be able to explain the concept of needs and wants as used in day to day life."},
                        {"name": "Analyse types of economic resources", "description": "By the end of the lesson, the learner should be able to analyse the types of economic resources in satisfaction of human needs and wants."},
                        {"name": "Investigate the importance of business activities", "description": "By the end of the lesson, the learner should be able to investigate the importance of business activities in the society."},
                        {"name": "Classify business activities in an economy", "description": "By the end of the lesson, the learner should be able to classify business activities in an economy."},
                        {"name": "Examine micro and macro factors affecting business", "description": "By the end of the lesson, the learner should be able to examine the micro and macro factors that affect business activities."},
                        {"name": "Appreciate the importance of business activities", "description": "By the end of the lesson, the learner should be able to appreciate the importance of business activities in an economy."}
                    ]
                },
                {
                    "name": "Types of Business Ownership",
                    "slos": [
                        {"name": "Explore sole proprietorship business", "description": "By the end of the lesson, the learner should be able to explore the formation, management, sources of finance, advantages, and disadvantages of a sole proprietorship business enterprise in Kenya."},
                        {"name": "Examine partnership business", "description": "By the end of the lesson, the learner should be able to examine the formation, management, sources of finance, advantages, and disadvantages of a partnership business enterprise in Kenya."},
                        {"name": "Analyse cooperative societies", "description": "By the end of the lesson, the learner should be able to analyse the formation, types, management, sources of finance, advantages, and disadvantages of a cooperative for economic growth."},
                        {"name": "Acknowledge role of business types in economy", "description": "By the end of the lesson, the learner should be able to acknowledge the role of sole proprietorship, partnerships and cooperative societies in the economy."}
                    ]
                },
                {
                    "name": "Social Responsibility of Business",
                    "slos": [
                        {"name": "Justify the need for social responsibility", "description": "By the end of the lesson, the learner should be able to justify the need for social responsibility of a business in the society."},
                        {"name": "Examine social responsibility activities", "description": "By the end of the lesson, the learner should be able to examine social responsibility activities of a business in the community."},
                        {"name": "Analyse challenges in social responsibilities", "description": "By the end of the lesson, the learner should be able to analyse the challenges faced by businesses when carrying out social responsibilities."},
                        {"name": "Design and implement social responsibility activity", "description": "By the end of the lesson, the learner should be able to design and implement a social responsibility activity in the school."},
                        {"name": "Appreciate business social responsibility", "description": "By the end of the lesson, the learner should be able to appreciate the need for business social responsibility in the society and the environment."}
                    ]
                },
                {
                    "name": "Entrepreneurship",
                    "slos": [
                        {"name": "Assess entrepreneurial skills for economic growth", "description": "By the end of the lesson, the learner should be able to assess the entrepreneurial skills for economic growth."},
                        {"name": "Examine types of entrepreneurs", "description": "By the end of the lesson, the learner should be able to examine the types of entrepreneurs in business."},
                        {"name": "Evaluate business ideas and opportunities", "description": "By the end of the lesson, the learner should be able to evaluate business ideas and opportunities for business start-ups."},
                        {"name": "Justify the importance of incubation", "description": "By the end of the lesson, the learner should be able to justify the importance of incubation for business growth."},
                        {"name": "Identify opportunity and start a business", "description": "By the end of the lesson, the learner should be able to identify an opportunity and start a business in school."},
                        {"name": "Embrace entrepreneurial skills", "description": "By the end of the lesson, the learner should be able to embrace entrepreneurial skills in business start-ups."}
                    ]
                },
                {
                    "name": "Production",
                    "slos": [
                        {"name": "Analyse the importance of production", "description": "By the end of the lesson, the learner should be able to analyse the importance of production in an economy."},
                        {"name": "Explain factors of production", "description": "By the end of the lesson, the learner should be able to explain factors of production required to produce goods and services."},
                        {"name": "Determine types of costs in production", "description": "By the end of the lesson, the learner should be able to determine the types of costs in a production unit."},
                        {"name": "Analyse division of labour and specialization", "description": "By the end of the lesson, the learner should be able to analyse the concept of the division of labour and specialization in production."},
                        {"name": "Examine roles of producer to consumer", "description": "By the end of the lesson, the learner should be able to examine the roles and responsibilities of a producer to consumer."},
                        {"name": "Design an appropriate product label", "description": "By the end of the lesson, the learner should be able to design an appropriate label for a product."},
                        {"name": "Recognize the role of production", "description": "By the end of the lesson, the learner should be able to recognize the role of production in an economy."}
                    ]
                },
                {
                    "name": "Consumer Satisfaction",
                    "slos": [
                        {"name": "Explore importance of consumer satisfaction", "description": "By the end of the lesson, the learner should be able to explore the importance of consumer satisfaction in business."},
                        {"name": "Examine terms and conditions for supply", "description": "By the end of the lesson, the learner should be able to examine the terms and conditions for the supply of goods and services to a consumer."},
                        {"name": "Justify remedies for consumer satisfaction", "description": "By the end of the lesson, the learner should be able to justify the remedies for consumer satisfaction."},
                        {"name": "Carry out customer satisfaction survey", "description": "By the end of the lesson, the learner should be able to carry out a customer satisfaction survey for improvement of service delivery."},
                        {"name": "Embrace importance of customer satisfaction", "description": "By the end of the lesson, the learner should be able to embrace the importance of customer satisfaction for business sustainability."}
                    ]
                }
            ]
        },
        {
            "name": "Government and Global Influence in Business",
            "substrands": [
                {
                    "name": "Public Finance",
                    "slos": [
                        {"name": "Explain the importance of public finance", "description": "By the end of the lesson, the learner should be able to explain the importance of public finance in Kenya."},
                        {"name": "Assess the concept of taxation", "description": "By the end of the lesson, the learner should be able to assess the concept of taxation in Kenya."},
                        {"name": "Analyse types of custom duties", "description": "By the end of the lesson, the learner should be able to analyse the types of custom duties in Kenya."},
                        {"name": "Evaluate trends in taxation", "description": "By the end of the lesson, the learner should be able to evaluate the trends in taxation in Kenya."},
                        {"name": "Identify ethical issues in taxation", "description": "By the end of the lesson, the learner should be able to identify ethical issues in taxation."},
                        {"name": "Write an article on importance of taxation", "description": "By the end of the lesson, the learner should be able to write an article on importance of taxation in Kenya to sensitize the community."},
                        {"name": "Appreciate the role of public finance", "description": "By the end of the lesson, the learner should be able to appreciate the role of public finance in Kenya."}
                    ]
                },
                {
                    "name": "International Trade",
                    "slos": [
                        {"name": "Examine the concept of international trade", "description": "By the end of the lesson, the learner should be able to examine the concept of international trade in an economy."},
                        {"name": "Explore limitations of international trade", "description": "By the end of the lesson, the learner should be able to explore the limitations of international trade to a country."},
                        {"name": "Analyse terms of sale and payments", "description": "By the end of the lesson, the learner should be able to analyse the terms of sale and payments used in international trade."},
                        {"name": "Explore digital applications in trade", "description": "By the end of the lesson, the learner should be able to explore digital applications in international trade."},
                        {"name": "Map local products for export", "description": "By the end of the lesson, the learner should be able to map the local products that can be developed for export."},
                        {"name": "Appreciate importance of international trade", "description": "By the end of the lesson, the learner should be able to appreciate the importance of international trade in an economy."}
                    ]
                }
            ]
        },
        {
            "name": "Financial Records in Business",
            "substrands": [
                {
                    "name": "Business Transactions",
                    "slos": [
                        {"name": "Explain the meaning of business transactions", "description": "By the end of the lesson, the learner should be able to explain the meaning of business transactions."},
                        {"name": "Classify types of business transactions", "description": "By the end of the lesson, the learner should be able to classify types of business transactions."},
                        {"name": "Record business transactions", "description": "By the end of the lesson, the learner should be able to record business transactions."},
                        {"name": "Appreciate importance of recording transactions", "description": "By the end of the lesson, the learner should be able to appreciate importance of recording business transactions."}
                    ]
                },
                {
                    "name": "Effects of Business Transactions",
                    "slos": [
                        {"name": "Explain the accounting equation", "description": "By the end of the lesson, the learner should be able to explain the accounting equation."},
                        {"name": "Analyse effects of transactions on equation", "description": "By the end of the lesson, the learner should be able to analyse effects of business transactions on the accounting equation."},
                        {"name": "Prepare simple accounting equation", "description": "By the end of the lesson, the learner should be able to prepare simple accounting equation."},
                        {"name": "Appreciate the accounting equation", "description": "By the end of the lesson, the learner should be able to appreciate the accounting equation."}
                    ]
                },
                {
                    "name": "Source Documents and Journals",
                    "slos": [
                        {"name": "Identify source documents", "description": "By the end of the lesson, the learner should be able to identify source documents used in business."},
                        {"name": "Describe the uses of source documents", "description": "By the end of the lesson, the learner should be able to describe the uses of source documents in business."},
                        {"name": "Explain books of original entry", "description": "By the end of the lesson, the learner should be able to explain books of original entry."},
                        {"name": "Record transactions in journals", "description": "By the end of the lesson, the learner should be able to record transactions in journals."},
                        {"name": "Appreciate the use of journals", "description": "By the end of the lesson, the learner should be able to appreciate the use of journals in business."}
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# CHRISTIAN RELIGIOUS EDUCATION (CRE)
# ============================================================================
CRE_DATA = {
    "strands": [
        {
            "name": "The Old Testament",
            "substrands": [
                {
                    "name": "The Holy Bible",
                    "slos": [
                        {"name": "Describe the Bible as inspired word of God", "description": "By the end of the lesson, the learner should be able to describe the Bible as the 'inspired' word of God."},
                        {"name": "Identify human authors of the Bible", "description": "By the end of the lesson, the learner should be able to identify human authors inspired to write the Holy Bible."},
                        {"name": "Organise Old Testament books by categories", "description": "By the end of the lesson, the learner should be able to organise the Old Testament books according to their categories."},
                        {"name": "Distinguish literary forms in the Bible", "description": "By the end of the lesson, the learner should be able to distinguish the literary forms used in writing the Bible."},
                        {"name": "Utilise poetic form to present a Psalm", "description": "By the end of the lesson, the learner should be able to utilise the poetic form and present a song from the book of Psalms."},
                        {"name": "Acknowledge the Bible is inspired", "description": "By the end of the lesson, the learner should be able to acknowledge that the Bible is the inspired word of God."}
                    ]
                },
                {
                    "name": "Methods of Studying the Holy Bible",
                    "slos": [
                        {"name": "Summarize five methods of studying Bible", "description": "By the end of the lesson, the learner should be able to summarize five methods of studying the Holy Bible."},
                        {"name": "Examine benefits of studying the Bible", "description": "By the end of the lesson, the learner should be able to examine the benefits of studying the Holy Bible."},
                        {"name": "Apply inductive method to Bible texts", "description": "By the end of the lesson, the learner should be able to apply inductive method of studying the Bible to specific Bible texts."},
                        {"name": "Utilise biography method for book of Jonah", "description": "By the end of the lesson, the learner should be able to utilise biography method to study the book of Jonah."},
                        {"name": "Desire to read God's word daily", "description": "By the end of the lesson, the learner should be able to desire to read the word of God daily to grow spiritually."}
                    ]
                },
                {
                    "name": "Redemption after the Fall of Man",
                    "slos": [
                        {"name": "Explain the account of creation", "description": "By the end of the lesson, the learner should be able to explain the account of creation as given in Genesis."},
                        {"name": "Describe the nature of human beings", "description": "By the end of the lesson, the learner should be able to describe the nature of human beings according to creation account."},
                        {"name": "Analyse the fall of man", "description": "By the end of the lesson, the learner should be able to analyse the fall of man and its consequences."},
                        {"name": "Explain God's plan for redemption", "description": "By the end of the lesson, the learner should be able to explain God's plan for the redemption of humankind."},
                        {"name": "Appreciate God's redemption plan", "description": "By the end of the lesson, the learner should be able to appreciate God's plan for redemption."}
                    ]
                },
                {
                    "name": "Stewardship over Creation",
                    "slos": [
                        {"name": "Explain the meaning of stewardship", "description": "By the end of the lesson, the learner should be able to explain the meaning of stewardship over creation."},
                        {"name": "Describe responsibilities of stewards", "description": "By the end of the lesson, the learner should be able to describe the responsibilities of human beings as stewards of creation."},
                        {"name": "Analyse environmental challenges", "description": "By the end of the lesson, the learner should be able to analyse environmental challenges facing the world today."},
                        {"name": "Propose solutions to environmental problems", "description": "By the end of the lesson, the learner should be able to propose solutions to environmental problems."},
                        {"name": "Embrace stewardship responsibilities", "description": "By the end of the lesson, the learner should be able to embrace responsibilities of stewardship over creation."}
                    ]
                },
                {
                    "name": "The Exodus",
                    "slos": [
                        {"name": "Describe the life of Moses", "description": "By the end of the lesson, the learner should be able to describe the life of Moses in Egypt and in Midian."},
                        {"name": "Explain the call of Moses", "description": "By the end of the lesson, the learner should be able to explain the call of Moses at the burning bush."},
                        {"name": "Analyse the ten plagues", "description": "By the end of the lesson, the learner should be able to analyse the ten plagues in Egypt."},
                        {"name": "Describe the Passover", "description": "By the end of the lesson, the learner should be able to describe the Passover event and its significance."},
                        {"name": "Relate Exodus to contemporary situations", "description": "By the end of the lesson, the learner should be able to relate the Exodus experience to contemporary situations."}
                    ]
                },
                {
                    "name": "The Sinai Covenant",
                    "slos": [
                        {"name": "Explain the meaning of covenant", "description": "By the end of the lesson, the learner should be able to explain the meaning of covenant in the Bible."},
                        {"name": "Describe the Sinai Covenant", "description": "By the end of the lesson, the learner should be able to describe the making of the Sinai Covenant."},
                        {"name": "Analyse the Ten Commandments", "description": "By the end of the lesson, the learner should be able to analyse the Ten Commandments and their relevance today."},
                        {"name": "Examine Israel's breaking of covenant", "description": "By the end of the lesson, the learner should be able to examine how the Israelites broke the covenant."},
                        {"name": "Apply covenant principles in daily life", "description": "By the end of the lesson, the learner should be able to apply covenant principles in daily life."}
                    ]
                },
                {
                    "name": "Loyalty to God (Elijah)",
                    "slos": [
                        {"name": "Describe the background of Prophet Elijah", "description": "By the end of the lesson, the learner should be able to describe the background of Prophet Elijah."},
                        {"name": "Analyse Elijah's contest on Mt. Carmel", "description": "By the end of the lesson, the learner should be able to analyse Elijah's contest with prophets of Baal on Mt. Carmel."},
                        {"name": "Examine Elijah's encounter at Mt. Horeb", "description": "By the end of the lesson, the learner should be able to examine Elijah's encounter with God at Mt. Horeb."},
                        {"name": "Relate Elijah's loyalty to Christian life", "description": "By the end of the lesson, the learner should be able to relate Elijah's loyalty to God to the Christian life today."},
                        {"name": "Embrace loyalty to God", "description": "By the end of the lesson, the learner should be able to embrace loyalty to God in all situations."}
                    ]
                },
                {
                    "name": "The Old Testament Prophecies",
                    "slos": [
                        {"name": "Explain the role of prophets", "description": "By the end of the lesson, the learner should be able to explain the role of prophets in the Old Testament."},
                        {"name": "Describe messianic prophecies", "description": "By the end of the lesson, the learner should be able to describe messianic prophecies in the Old Testament."},
                        {"name": "Analyse fulfillment of prophecies", "description": "By the end of the lesson, the learner should be able to analyse how the prophecies were fulfilled in Jesus Christ."},
                        {"name": "Appreciate prophetic mission", "description": "By the end of the lesson, the learner should be able to appreciate the prophetic mission in society today."}
                    ]
                },
                {
                    "name": "Background of Prophet Amos",
                    "slos": [
                        {"name": "Describe the background of Amos", "description": "By the end of the lesson, the learner should be able to describe the background of Prophet Amos."},
                        {"name": "Explain the call of Amos", "description": "By the end of the lesson, the learner should be able to explain the call of Amos to prophetic ministry."},
                        {"name": "Analyse social and religious conditions", "description": "By the end of the lesson, the learner should be able to analyse the social and religious conditions during the time of Amos."},
                        {"name": "Relate Amos's background to today", "description": "By the end of the lesson, the learner should be able to relate Amos's background to situations in society today."}
                    ]
                },
                {
                    "name": "Teachings of Prophet Amos",
                    "slos": [
                        {"name": "Analyse Amos's teachings on social justice", "description": "By the end of the lesson, the learner should be able to analyse Amos's teachings on social justice."},
                        {"name": "Examine teachings on religious hypocrisy", "description": "By the end of the lesson, the learner should be able to examine Amos's teachings on religious hypocrisy."},
                        {"name": "Describe teachings on Day of the Lord", "description": "By the end of the lesson, the learner should be able to describe Amos's teachings on the Day of the Lord."},
                        {"name": "Apply Amos's teachings today", "description": "By the end of the lesson, the learner should be able to apply Amos's teachings in society today."}
                    ]
                }
            ]
        },
        {
            "name": "The New Testament",
            "substrands": [
                {
                    "name": "The New Testament Books",
                    "slos": [
                        {"name": "Organise New Testament books by categories", "description": "By the end of the lesson, the learner should be able to organise the New Testament books according to their categories."},
                        {"name": "Explain formation of New Testament", "description": "By the end of the lesson, the learner should be able to explain the formation of the New Testament."},
                        {"name": "Distinguish between Gospel accounts", "description": "By the end of the lesson, the learner should be able to distinguish between the four Gospel accounts."},
                        {"name": "Appreciate the New Testament", "description": "By the end of the lesson, the learner should be able to appreciate the significance of the New Testament."}
                    ]
                },
                {
                    "name": "Infancy and Early Life of Jesus Christ",
                    "slos": [
                        {"name": "Describe birth announcements", "description": "By the end of the lesson, the learner should be able to describe the announcements of the births of John the Baptist and Jesus."},
                        {"name": "Explain the birth of Jesus", "description": "By the end of the lesson, the learner should be able to explain the birth of Jesus Christ."},
                        {"name": "Analyse Jesus's presentation in the temple", "description": "By the end of the lesson, the learner should be able to analyse the presentation of Jesus in the temple."},
                        {"name": "Describe Jesus in the temple at twelve", "description": "By the end of the lesson, the learner should be able to describe Jesus at the temple at the age of twelve."},
                        {"name": "Embrace values from Jesus's early life", "description": "By the end of the lesson, the learner should be able to embrace values from the early life of Jesus."}
                    ]
                },
                {
                    "name": "Galilean Ministry",
                    "slos": [
                        {"name": "Describe Jesus's baptism and temptation", "description": "By the end of the lesson, the learner should be able to describe Jesus's baptism and temptation."},
                        {"name": "Explain the calling of disciples", "description": "By the end of the lesson, the learner should be able to explain the calling of the first disciples."},
                        {"name": "Analyse miracles of Jesus", "description": "By the end of the lesson, the learner should be able to analyse the miracles of Jesus in Galilee."},
                        {"name": "Examine teachings of Jesus", "description": "By the end of the lesson, the learner should be able to examine the teachings of Jesus in Galilee."},
                        {"name": "Apply lessons from Galilean ministry", "description": "By the end of the lesson, the learner should be able to apply lessons from Jesus's Galilean ministry."}
                    ]
                },
                {
                    "name": "Paul's First Letter to the Corinthians",
                    "slos": [
                        {"name": "Describe background of Corinthian church", "description": "By the end of the lesson, the learner should be able to describe the background of the church in Corinth."},
                        {"name": "Analyse Paul's teachings on unity", "description": "By the end of the lesson, the learner should be able to analyse Paul's teachings on unity in the church."},
                        {"name": "Examine teachings on spiritual gifts", "description": "By the end of the lesson, the learner should be able to examine Paul's teachings on spiritual gifts."},
                        {"name": "Apply Paul's teachings in daily life", "description": "By the end of the lesson, the learner should be able to apply Paul's teachings in daily Christian life."}
                    ]
                }
            ]
        },
        {
            "name": "Church in Action",
            "substrands": [
                {
                    "name": "The Holy Spirit",
                    "slos": [
                        {"name": "Explain the meaning of Holy Spirit", "description": "By the end of the lesson, the learner should be able to explain the meaning of the Holy Spirit."},
                        {"name": "Describe the coming of Holy Spirit", "description": "By the end of the lesson, the learner should be able to describe the coming of the Holy Spirit at Pentecost."},
                        {"name": "Analyse the work of Holy Spirit", "description": "By the end of the lesson, the learner should be able to analyse the work of the Holy Spirit in the early church."},
                        {"name": "Relate Holy Spirit to Christian life", "description": "By the end of the lesson, the learner should be able to relate the work of the Holy Spirit to Christian life today."}
                    ]
                },
                {
                    "name": "The Gifts of the Holy Spirit",
                    "slos": [
                        {"name": "Identify gifts of the Holy Spirit", "description": "By the end of the lesson, the learner should be able to identify the gifts of the Holy Spirit."},
                        {"name": "Distinguish between gifts and fruits", "description": "By the end of the lesson, the learner should be able to distinguish between gifts and fruits of the Holy Spirit."},
                        {"name": "Analyse use of gifts in the church", "description": "By the end of the lesson, the learner should be able to analyse the use of spiritual gifts in the church."},
                        {"name": "Embrace spiritual gifts", "description": "By the end of the lesson, the learner should be able to embrace the use of spiritual gifts for the good of others."}
                    ]
                },
                {
                    "name": "The Holy Trinity",
                    "slos": [
                        {"name": "Explain the doctrine of Trinity", "description": "By the end of the lesson, the learner should be able to explain the doctrine of the Trinity."},
                        {"name": "Describe the relationship in Trinity", "description": "By the end of the lesson, the learner should be able to describe the relationship between Father, Son, and Holy Spirit."},
                        {"name": "Appreciate the mystery of Trinity", "description": "By the end of the lesson, the learner should be able to appreciate the mystery of the Holy Trinity."}
                    ]
                },
                {
                    "name": "Sacraments",
                    "slos": [
                        {"name": "Explain the meaning of sacraments", "description": "By the end of the lesson, the learner should be able to explain the meaning of sacraments."},
                        {"name": "Describe Christian sacraments", "description": "By the end of the lesson, the learner should be able to describe Christian sacraments and their significance."},
                        {"name": "Analyse sacrament of baptism", "description": "By the end of the lesson, the learner should be able to analyse the sacrament of baptism."},
                        {"name": "Examine the Lord's Supper", "description": "By the end of the lesson, the learner should be able to examine the significance of the Lord's Supper."},
                        {"name": "Appreciate sacraments in Christian life", "description": "By the end of the lesson, the learner should be able to appreciate the role of sacraments in Christian life."}
                    ]
                }
            ]
        },
        {
            "name": "Christian Living Today",
            "substrands": [
                {
                    "name": "Christian Ethics",
                    "slos": [
                        {"name": "Explain the meaning of Christian ethics", "description": "By the end of the lesson, the learner should be able to explain the meaning of Christian ethics."},
                        {"name": "Analyse sources of Christian ethics", "description": "By the end of the lesson, the learner should be able to analyse sources of Christian ethics."},
                        {"name": "Examine ethical issues facing Christians", "description": "By the end of the lesson, the learner should be able to examine ethical issues facing Christians today."},
                        {"name": "Apply Christian ethics in daily life", "description": "By the end of the lesson, the learner should be able to apply Christian ethics in daily life."}
                    ]
                },
                {
                    "name": "Human Rights (Non-discrimination)",
                    "slos": [
                        {"name": "Explain the concept of human rights", "description": "By the end of the lesson, the learner should be able to explain the concept of human rights from a Christian perspective."},
                        {"name": "Analyse discrimination in society", "description": "By the end of the lesson, the learner should be able to analyse forms of discrimination in society."},
                        {"name": "Examine Christian response to discrimination", "description": "By the end of the lesson, the learner should be able to examine Christian response to discrimination."},
                        {"name": "Promote human rights", "description": "By the end of the lesson, the learner should be able to promote respect for human rights in society."}
                    ]
                },
                {
                    "name": "Human Sexuality",
                    "slos": [
                        {"name": "Explain the Christian view of sexuality", "description": "By the end of the lesson, the learner should be able to explain the Christian view of human sexuality."},
                        {"name": "Analyse challenges to sexual purity", "description": "By the end of the lesson, the learner should be able to analyse challenges to sexual purity today."},
                        {"name": "Examine Christian response to sexuality", "description": "By the end of the lesson, the learner should be able to examine Christian response to issues of sexuality."},
                        {"name": "Embrace sexual purity", "description": "By the end of the lesson, the learner should be able to embrace sexual purity as a Christian value."}
                    ]
                },
                {
                    "name": "Marriage and Family",
                    "slos": [
                        {"name": "Explain the Christian view of marriage", "description": "By the end of the lesson, the learner should be able to explain the Christian view of marriage."},
                        {"name": "Analyse the roles in a Christian family", "description": "By the end of the lesson, the learner should be able to analyse the roles of members in a Christian family."},
                        {"name": "Examine challenges facing families", "description": "By the end of the lesson, the learner should be able to examine challenges facing Christian families today."},
                        {"name": "Appreciate Christian family values", "description": "By the end of the lesson, the learner should be able to appreciate Christian family values."}
                    ]
                },
                {
                    "name": "Christian Response to Modern Science and Technology",
                    "slos": [
                        {"name": "Explain relationship between faith and science", "description": "By the end of the lesson, the learner should be able to explain the relationship between Christian faith and science."},
                        {"name": "Analyse ethical issues in technology", "description": "By the end of the lesson, the learner should be able to analyse ethical issues arising from technology."},
                        {"name": "Examine Christian response to science", "description": "By the end of the lesson, the learner should be able to examine Christian response to modern scientific developments."},
                        {"name": "Use technology responsibly", "description": "By the end of the lesson, the learner should be able to use technology responsibly as a Christian."}
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# ELECTRICAL TECHNOLOGY
# ============================================================================
ELECTRICAL_TECHNOLOGY_DATA = {
    "strands": [
        {
            "name": "Fundamentals of Electrical Technology",
            "substrands": [
                {
                    "name": "Introduction to Electrical Technology",
                    "slos": [
                        {"name": "Explain the importance of electrical technology", "description": "By the end of the lesson, the learner should be able to explain the importance of electrical technology in society."},
                        {"name": "Identify career opportunities", "description": "By the end of the lesson, the learner should be able to identify career opportunities in the electrical technology field."},
                        {"name": "Apply safety regulations", "description": "By the end of the lesson, the learner should be able to apply safety regulations while carrying out electrical tasks."},
                        {"name": "Explain roles of stakeholders in safety", "description": "By the end of the lesson, the learner should be able to explain the roles of stakeholders in application of electrical safety."},
                        {"name": "Embrace electrical technology as a career", "description": "By the end of the lesson, the learner should be able to embrace electrical technology as a career in society."}
                    ]
                },
                {
                    "name": "D.C Electric Circuit",
                    "slos": [
                        {"name": "Explain basic electrical quantities", "description": "By the end of the lesson, the learner should be able to explain basic electrical quantities."},
                        {"name": "Apply Ohm's law in calculations", "description": "By the end of the lesson, the learner should be able to apply Ohm's law in electrical calculations."},
                        {"name": "Analyse series and parallel circuits", "description": "By the end of the lesson, the learner should be able to analyse series and parallel circuits."},
                        {"name": "Calculate power and energy", "description": "By the end of the lesson, the learner should be able to calculate power and energy in D.C circuits."},
                        {"name": "Construct simple D.C circuits", "description": "By the end of the lesson, the learner should be able to construct simple D.C circuits."}
                    ]
                },
                {
                    "name": "Capacitors and Capacitance",
                    "slos": [
                        {"name": "Explain the concept of capacitance", "description": "By the end of the lesson, the learner should be able to explain the concept of capacitance."},
                        {"name": "Describe types of capacitors", "description": "By the end of the lesson, the learner should be able to describe types of capacitors."},
                        {"name": "Calculate capacitance in circuits", "description": "By the end of the lesson, the learner should be able to calculate capacitance in series and parallel circuits."},
                        {"name": "Apply capacitors in practical circuits", "description": "By the end of the lesson, the learner should be able to apply capacitors in practical circuits."}
                    ]
                },
                {
                    "name": "Cells and Batteries",
                    "slos": [
                        {"name": "Explain the concept of cells and batteries", "description": "By the end of the lesson, the learner should be able to explain the concept of cells and batteries."},
                        {"name": "Classify types of cells", "description": "By the end of the lesson, the learner should be able to classify types of cells and batteries."},
                        {"name": "Connect cells in series and parallel", "description": "By the end of the lesson, the learner should be able to connect cells in series and parallel configurations."},
                        {"name": "Maintain cells and batteries", "description": "By the end of the lesson, the learner should be able to maintain cells and batteries properly."}
                    ]
                }
            ]
        },
        {
            "name": "Electrical Machines",
            "substrands": [
                {
                    "name": "Magnetism",
                    "slos": [
                        {"name": "Explain the concept of magnetism", "description": "By the end of the lesson, the learner should be able to explain the concept of magnetism."},
                        {"name": "Describe properties of magnets", "description": "By the end of the lesson, the learner should be able to describe properties of magnets."},
                        {"name": "Analyse magnetic fields", "description": "By the end of the lesson, the learner should be able to analyse magnetic fields and flux patterns."},
                        {"name": "Apply magnetism in practical situations", "description": "By the end of the lesson, the learner should be able to apply magnetism in practical situations."}
                    ]
                },
                {
                    "name": "Electromagnetism",
                    "slos": [
                        {"name": "Explain the concept of electromagnetism", "description": "By the end of the lesson, the learner should be able to explain the concept of electromagnetism."},
                        {"name": "Describe electromagnetic induction", "description": "By the end of the lesson, the learner should be able to describe electromagnetic induction."},
                        {"name": "Analyse applications of electromagnetism", "description": "By the end of the lesson, the learner should be able to analyse applications of electromagnetism."},
                        {"name": "Construct simple electromagnets", "description": "By the end of the lesson, the learner should be able to construct simple electromagnets."}
                    ]
                },
                {
                    "name": "Measuring Instruments",
                    "slos": [
                        {"name": "Identify electrical measuring instruments", "description": "By the end of the lesson, the learner should be able to identify electrical measuring instruments."},
                        {"name": "Explain the working principle of meters", "description": "By the end of the lesson, the learner should be able to explain the working principle of electrical meters."},
                        {"name": "Use measuring instruments correctly", "description": "By the end of the lesson, the learner should be able to use measuring instruments correctly."},
                        {"name": "Interpret meter readings", "description": "By the end of the lesson, the learner should be able to interpret meter readings accurately."}
                    ]
                }
            ]
        },
        {
            "name": "Electrical Installation",
            "substrands": [
                {
                    "name": "Generation, Transmission and Distribution of Electricity",
                    "slos": [
                        {"name": "Explain methods of electricity generation", "description": "By the end of the lesson, the learner should be able to explain methods of electricity generation."},
                        {"name": "Describe transmission of electricity", "description": "By the end of the lesson, the learner should be able to describe the transmission of electricity."},
                        {"name": "Analyse distribution systems", "description": "By the end of the lesson, the learner should be able to analyse electricity distribution systems."},
                        {"name": "Appreciate importance of electricity", "description": "By the end of the lesson, the learner should be able to appreciate the importance of electricity in society."}
                    ]
                },
                {
                    "name": "Equipment at the Intake Point",
                    "slos": [
                        {"name": "Identify intake point equipment", "description": "By the end of the lesson, the learner should be able to identify equipment at the intake point."},
                        {"name": "Explain functions of intake equipment", "description": "By the end of the lesson, the learner should be able to explain the functions of intake equipment."},
                        {"name": "Install intake equipment", "description": "By the end of the lesson, the learner should be able to install intake equipment correctly."},
                        {"name": "Maintain intake equipment", "description": "By the end of the lesson, the learner should be able to maintain intake equipment."}
                    ]
                },
                {
                    "name": "Final Circuits",
                    "slos": [
                        {"name": "Explain types of final circuits", "description": "By the end of the lesson, the learner should be able to explain types of final circuits."},
                        {"name": "Design final circuits", "description": "By the end of the lesson, the learner should be able to design final circuits for different applications."},
                        {"name": "Install final circuits", "description": "By the end of the lesson, the learner should be able to install final circuits correctly."},
                        {"name": "Test and commission final circuits", "description": "By the end of the lesson, the learner should be able to test and commission final circuits."}
                    ]
                }
            ]
        },
        {
            "name": "Electronics",
            "substrands": [
                {
                    "name": "Semiconductor Theory",
                    "slos": [
                        {"name": "Explain the concept of semiconductors", "description": "By the end of the lesson, the learner should be able to explain the concept of semiconductors."},
                        {"name": "Describe types of semiconductors", "description": "By the end of the lesson, the learner should be able to describe types of semiconductors."},
                        {"name": "Analyse semiconductor properties", "description": "By the end of the lesson, the learner should be able to analyse semiconductor properties."},
                        {"name": "Apply semiconductor theory", "description": "By the end of the lesson, the learner should be able to apply semiconductor theory in electronics."}
                    ]
                },
                {
                    "name": "Semiconductor Diodes",
                    "slos": [
                        {"name": "Explain the working of diodes", "description": "By the end of the lesson, the learner should be able to explain the working of semiconductor diodes."},
                        {"name": "Identify types of diodes", "description": "By the end of the lesson, the learner should be able to identify types of semiconductor diodes."},
                        {"name": "Test diodes", "description": "By the end of the lesson, the learner should be able to test semiconductor diodes."},
                        {"name": "Apply diodes in circuits", "description": "By the end of the lesson, the learner should be able to apply diodes in practical circuits."}
                    ]
                },
                {
                    "name": "Transistors",
                    "slos": [
                        {"name": "Explain the working of transistors", "description": "By the end of the lesson, the learner should be able to explain the working of transistors."},
                        {"name": "Identify types of transistors", "description": "By the end of the lesson, the learner should be able to identify types of transistors."},
                        {"name": "Test transistors", "description": "By the end of the lesson, the learner should be able to test transistors."},
                        {"name": "Apply transistors in circuits", "description": "By the end of the lesson, the learner should be able to apply transistors in practical circuits."}
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# FINE ARTS
# ============================================================================
FINE_ARTS_DATA = {
    "strands": [
        {
            "name": "Picture Making Techniques (2D Art)",
            "substrands": [
                {
                    "name": "Drawing",
                    "slos": [
                        {"name": "Analyze elements and principles of 2D art", "description": "By the end of the lesson, the learner should be able to analyze the elements and principles of 2 dimensional art in drawing."},
                        {"name": "Draw objects in one-point perspective", "description": "By the end of the lesson, the learner should be able to draw objects in one-point perspective."},
                        {"name": "Draw objects in two-point perspective", "description": "By the end of the lesson, the learner should be able to draw objects in two-point perspective."},
                        {"name": "Apply stages of drawing in still life", "description": "By the end of the lesson, the learner should be able to apply the stages of drawing in executing a still life composition."},
                        {"name": "Make a portfolio folder", "description": "By the end of the lesson, the learner should be able to make a portfolio folder for storage and presentation of artworks."}
                    ]
                },
                {
                    "name": "Painting",
                    "slos": [
                        {"name": "Explore colour theory", "description": "By the end of the lesson, the learner should be able to explore colour theory in painting."},
                        {"name": "Apply painting techniques", "description": "By the end of the lesson, the learner should be able to apply various painting techniques."},
                        {"name": "Create paintings using different media", "description": "By the end of the lesson, the learner should be able to create paintings using different media."},
                        {"name": "Appreciate paintings from different cultures", "description": "By the end of the lesson, the learner should be able to appreciate paintings from different cultures."}
                    ]
                },
                {
                    "name": "Collage",
                    "slos": [
                        {"name": "Explain the concept of collage", "description": "By the end of the lesson, the learner should be able to explain the concept of collage as an art form."},
                        {"name": "Identify materials for collage", "description": "By the end of the lesson, the learner should be able to identify materials suitable for collage making."},
                        {"name": "Create collage artworks", "description": "By the end of the lesson, the learner should be able to create collage artworks using various materials."},
                        {"name": "Display collage artworks", "description": "By the end of the lesson, the learner should be able to display collage artworks appropriately."}
                    ]
                }
            ]
        },
        {
            "name": "Multimedia Arts (2D Art)",
            "substrands": [
                {
                    "name": "Graphic Design",
                    "slos": [
                        {"name": "Explain the concept of graphic design", "description": "By the end of the lesson, the learner should be able to explain the concept of graphic design."},
                        {"name": "Identify elements of graphic design", "description": "By the end of the lesson, the learner should be able to identify elements of graphic design."},
                        {"name": "Create graphic design works", "description": "By the end of the lesson, the learner should be able to create graphic design works."},
                        {"name": "Apply digital tools in graphic design", "description": "By the end of the lesson, the learner should be able to apply digital tools in graphic design."}
                    ]
                },
                {
                    "name": "Fabric Decoration: Tie and Dye",
                    "slos": [
                        {"name": "Explain tie and dye technique", "description": "By the end of the lesson, the learner should be able to explain the tie and dye technique."},
                        {"name": "Identify materials for tie and dye", "description": "By the end of the lesson, the learner should be able to identify materials for tie and dye."},
                        {"name": "Create tie and dye patterns", "description": "By the end of the lesson, the learner should be able to create tie and dye patterns on fabric."},
                        {"name": "Apply tie and dye in functional items", "description": "By the end of the lesson, the learner should be able to apply tie and dye in making functional items."}
                    ]
                },
                {
                    "name": "Fabric Decoration: Batik",
                    "slos": [
                        {"name": "Explain batik technique", "description": "By the end of the lesson, the learner should be able to explain the batik technique."},
                        {"name": "Identify materials for batik", "description": "By the end of the lesson, the learner should be able to identify materials for batik."},
                        {"name": "Create batik designs", "description": "By the end of the lesson, the learner should be able to create batik designs on fabric."},
                        {"name": "Apply batik in functional items", "description": "By the end of the lesson, the learner should be able to apply batik in making functional items."}
                    ]
                }
            ]
        },
        {
            "name": "Indigenous Crafts (3D Art)",
            "substrands": [
                {
                    "name": "Pottery",
                    "slos": [
                        {"name": "Explain pottery as an art form", "description": "By the end of the lesson, the learner should be able to explain pottery as an art form."},
                        {"name": "Identify pottery techniques", "description": "By the end of the lesson, the learner should be able to identify pottery techniques."},
                        {"name": "Create pottery items", "description": "By the end of the lesson, the learner should be able to create pottery items using various techniques."},
                        {"name": "Decorate pottery items", "description": "By the end of the lesson, the learner should be able to decorate pottery items."}
                    ]
                },
                {
                    "name": "Sculpture",
                    "slos": [
                        {"name": "Explain sculpture as an art form", "description": "By the end of the lesson, the learner should be able to explain sculpture as an art form."},
                        {"name": "Identify sculpture techniques", "description": "By the end of the lesson, the learner should be able to identify sculpture techniques."},
                        {"name": "Create sculptures", "description": "By the end of the lesson, the learner should be able to create sculptures using various materials."},
                        {"name": "Display sculptures", "description": "By the end of the lesson, the learner should be able to display sculptures appropriately."}
                    ]
                },
                {
                    "name": "Weaving",
                    "slos": [
                        {"name": "Explain weaving as a craft", "description": "By the end of the lesson, the learner should be able to explain weaving as a craft."},
                        {"name": "Identify weaving materials", "description": "By the end of the lesson, the learner should be able to identify weaving materials."},
                        {"name": "Create woven items", "description": "By the end of the lesson, the learner should be able to create woven items."},
                        {"name": "Apply weaving in functional items", "description": "By the end of the lesson, the learner should be able to apply weaving in making functional items."}
                    ]
                },
                {
                    "name": "Jewellery and Ornamentation",
                    "slos": [
                        {"name": "Explain jewellery making", "description": "By the end of the lesson, the learner should be able to explain jewellery making as an art."},
                        {"name": "Identify jewellery making materials", "description": "By the end of the lesson, the learner should be able to identify materials for jewellery making."},
                        {"name": "Create jewellery items", "description": "By the end of the lesson, the learner should be able to create jewellery items."},
                        {"name": "Display jewellery items", "description": "By the end of the lesson, the learner should be able to display jewellery items appropriately."}
                    ]
                },
                {
                    "name": "Art Appreciation",
                    "slos": [
                        {"name": "Explain art appreciation", "description": "By the end of the lesson, the learner should be able to explain the concept of art appreciation."},
                        {"name": "Critique artworks", "description": "By the end of the lesson, the learner should be able to critique artworks objectively."},
                        {"name": "Appreciate diverse art forms", "description": "By the end of the lesson, the learner should be able to appreciate diverse art forms from different cultures."},
                        {"name": "Document and present artworks", "description": "By the end of the lesson, the learner should be able to document and present artworks."}
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# FRENCH
# ============================================================================
FRENCH_DATA = {
    "strands": [
        {
            "name": "Listening and Speaking",
            "substrands": [
                {
                    "name": "Informational Listening",
                    "slos": [
                        {"name": "Listen for specific information", "description": "By the end of the lesson, the learner should be able to listen for specific information in French."},
                        {"name": "Identify key details in audio", "description": "By the end of the lesson, the learner should be able to identify key details in French audio materials."},
                        {"name": "Respond to informational content", "description": "By the end of the lesson, the learner should be able to respond appropriately to informational content in French."}
                    ]
                },
                {
                    "name": "Responsive Listening",
                    "slos": [
                        {"name": "Listen and respond to instructions", "description": "By the end of the lesson, the learner should be able to listen and respond to instructions in French."},
                        {"name": "Follow oral directions", "description": "By the end of the lesson, the learner should be able to follow oral directions in French."},
                        {"name": "Demonstrate understanding through action", "description": "By the end of the lesson, the learner should be able to demonstrate understanding through appropriate action."}
                    ]
                },
                {
                    "name": "Comprehensive Listening",
                    "slos": [
                        {"name": "Understand spoken French", "description": "By the end of the lesson, the learner should be able to understand spoken French in various contexts."},
                        {"name": "Summarize spoken content", "description": "By the end of the lesson, the learner should be able to summarize spoken content in French."},
                        {"name": "Interpret meaning from context", "description": "By the end of the lesson, the learner should be able to interpret meaning from context."}
                    ]
                },
                {
                    "name": "Informative Speaking",
                    "slos": [
                        {"name": "Present information in French", "description": "By the end of the lesson, the learner should be able to present information in French."},
                        {"name": "Describe people, places and things", "description": "By the end of the lesson, the learner should be able to describe people, places and things in French."},
                        {"name": "Give instructions in French", "description": "By the end of the lesson, the learner should be able to give instructions in French."}
                    ]
                },
                {
                    "name": "Situational Speaking",
                    "slos": [
                        {"name": "Use appropriate French in situations", "description": "By the end of the lesson, the learner should be able to use appropriate French in various situations."},
                        {"name": "Engage in conversations", "description": "By the end of the lesson, the learner should be able to engage in conversations in French."},
                        {"name": "Express opinions in French", "description": "By the end of the lesson, the learner should be able to express opinions in French."}
                    ]
                }
            ]
        },
        {
            "name": "Reading",
            "substrands": [
                {
                    "name": "Extensive Reading",
                    "slos": [
                        {"name": "Read French texts for pleasure", "description": "By the end of the lesson, the learner should be able to read French texts for pleasure."},
                        {"name": "Develop reading fluency", "description": "By the end of the lesson, the learner should be able to develop reading fluency in French."},
                        {"name": "Build vocabulary through reading", "description": "By the end of the lesson, the learner should be able to build vocabulary through extensive reading."}
                    ]
                },
                {
                    "name": "Reading for Comprehension",
                    "slos": [
                        {"name": "Understand French texts", "description": "By the end of the lesson, the learner should be able to understand French texts."},
                        {"name": "Answer comprehension questions", "description": "By the end of the lesson, the learner should be able to answer comprehension questions in French."},
                        {"name": "Identify main ideas and details", "description": "By the end of the lesson, the learner should be able to identify main ideas and details in French texts."}
                    ]
                },
                {
                    "name": "Reading for Vocabulary",
                    "slos": [
                        {"name": "Learn new vocabulary through reading", "description": "By the end of the lesson, the learner should be able to learn new vocabulary through reading."},
                        {"name": "Use context clues for meaning", "description": "By the end of the lesson, the learner should be able to use context clues to determine word meaning."},
                        {"name": "Apply new vocabulary", "description": "By the end of the lesson, the learner should be able to apply new vocabulary in context."}
                    ]
                },
                {
                    "name": "Critical Reading",
                    "slos": [
                        {"name": "Analyse French texts critically", "description": "By the end of the lesson, the learner should be able to analyse French texts critically."},
                        {"name": "Evaluate information in texts", "description": "By the end of the lesson, the learner should be able to evaluate information in French texts."},
                        {"name": "Form opinions about texts", "description": "By the end of the lesson, the learner should be able to form and express opinions about French texts."}
                    ]
                }
            ]
        },
        {
            "name": "Writing",
            "substrands": [
                {
                    "name": "Descriptive Writing",
                    "slos": [
                        {"name": "Write descriptions in French", "description": "By the end of the lesson, the learner should be able to write descriptions in French."},
                        {"name": "Describe people and places", "description": "By the end of the lesson, the learner should be able to describe people and places in French."},
                        {"name": "Use descriptive vocabulary", "description": "By the end of the lesson, the learner should be able to use descriptive vocabulary effectively."}
                    ]
                },
                {
                    "name": "Expository Writing",
                    "slos": [
                        {"name": "Write expository texts", "description": "By the end of the lesson, the learner should be able to write expository texts in French."},
                        {"name": "Explain concepts in writing", "description": "By the end of the lesson, the learner should be able to explain concepts in French writing."},
                        {"name": "Organize ideas logically", "description": "By the end of the lesson, the learner should be able to organize ideas logically in French writing."}
                    ]
                },
                {
                    "name": "Process Writing",
                    "slos": [
                        {"name": "Write instructions in French", "description": "By the end of the lesson, the learner should be able to write instructions in French."},
                        {"name": "Describe processes", "description": "By the end of the lesson, the learner should be able to describe processes in French."},
                        {"name": "Use sequence words", "description": "By the end of the lesson, the learner should be able to use sequence words in French writing."}
                    ]
                },
                {
                    "name": "Persuasive Writing",
                    "slos": [
                        {"name": "Write persuasively in French", "description": "By the end of the lesson, the learner should be able to write persuasively in French."},
                        {"name": "Present arguments in writing", "description": "By the end of the lesson, the learner should be able to present arguments in French writing."},
                        {"name": "Use persuasive language", "description": "By the end of the lesson, the learner should be able to use persuasive language in French."}
                    ]
                },
                {
                    "name": "Informative Writing",
                    "slos": [
                        {"name": "Write informative texts", "description": "By the end of the lesson, the learner should be able to write informative texts in French."},
                        {"name": "Present facts clearly", "description": "By the end of the lesson, the learner should be able to present facts clearly in French writing."},
                        {"name": "Write reports in French", "description": "By the end of the lesson, the learner should be able to write reports in French."}
                    ]
                }
            ]
        },
        {
            "name": "Grammar",
            "substrands": [
                {
                    "name": "Pronouns and Conjunctions",
                    "slos": [
                        {"name": "Use French pronouns correctly", "description": "By the end of the lesson, the learner should be able to use French pronouns correctly."},
                        {"name": "Apply conjunctions in sentences", "description": "By the end of the lesson, the learner should be able to apply conjunctions in French sentences."},
                        {"name": "Construct complex sentences", "description": "By the end of the lesson, the learner should be able to construct complex sentences using pronouns and conjunctions."}
                    ]
                },
                {
                    "name": "Prepositions and Adjectives",
                    "slos": [
                        {"name": "Use French prepositions correctly", "description": "By the end of the lesson, the learner should be able to use French prepositions correctly."},
                        {"name": "Apply adjective agreement rules", "description": "By the end of the lesson, the learner should be able to apply adjective agreement rules in French."},
                        {"name": "Position adjectives correctly", "description": "By the end of the lesson, the learner should be able to position adjectives correctly in French sentences."}
                    ]
                },
                {
                    "name": "Verbs and Negation",
                    "slos": [
                        {"name": "Conjugate French verbs", "description": "By the end of the lesson, the learner should be able to conjugate French verbs in various tenses."},
                        {"name": "Use negation correctly", "description": "By the end of the lesson, the learner should be able to use negation correctly in French."},
                        {"name": "Form negative sentences", "description": "By the end of the lesson, the learner should be able to form negative sentences in French."}
                    ]
                },
                {
                    "name": "Infinitives and Imperatives",
                    "slos": [
                        {"name": "Use infinitive forms", "description": "By the end of the lesson, the learner should be able to use infinitive forms correctly in French."},
                        {"name": "Form imperative sentences", "description": "By the end of the lesson, the learner should be able to form imperative sentences in French."},
                        {"name": "Give commands in French", "description": "By the end of the lesson, the learner should be able to give commands in French."}
                    ]
                },
                {
                    "name": "Articles and Nouns",
                    "slos": [
                        {"name": "Use French articles correctly", "description": "By the end of the lesson, the learner should be able to use French articles correctly."},
                        {"name": "Apply gender rules for nouns", "description": "By the end of the lesson, the learner should be able to apply gender rules for French nouns."},
                        {"name": "Form plural nouns", "description": "By the end of the lesson, the learner should be able to form plural nouns in French."}
                    ]
                }
            ]
        }
    ]
}

# All subjects data
ALL_SUBJECTS = {
    "Business Studies": BUSINESS_STUDIES_DATA,
    "Christian Religious Education": CRE_DATA,
    "Electrical Technology": ELECTRICAL_TECHNOLOGY_DATA,
    "Fine Arts": FINE_ARTS_DATA,
    "French": FRENCH_DATA
}


async def seed_subject(subject_name, subject_data):
    """Seed a single subject with its strands, substrands, and SLOs"""
    print(f"\n{'='*60}")
    print(f"SEEDING: {subject_name}")
    print(f"{'='*60}")
    
    # Check if subject exists
    existing_subject = await db.subjects.find_one({"name": subject_name})
    if existing_subject:
        print(f"  [EXISTS] Subject '{subject_name}' already exists, updating...")
        subject_id = str(existing_subject["_id"])
    else:
        # Get Grade 10 ID
        grade = await db.grades.find_one({"name": {"$regex": "Grade 10", "$options": "i"}})
        if not grade:
            # Create Grade 10 if it doesn't exist
            result = await db.grades.insert_one({"name": "Grade 10", "order": 10})
            grade_id = str(result.inserted_id)
            print(f"  [CREATE] Created Grade 10")
        else:
            grade_id = str(grade["_id"])
        
        # Create subject
        result = await db.subjects.insert_one({
            "name": subject_name,
            "gradeIds": [grade_id]
        })
        subject_id = str(result.inserted_id)
        print(f"  [CREATE] Created subject: {subject_name}")
    
    # Process strands
    strands_count = 0
    substrands_count = 0
    slos_count = 0
    
    for strand_data in subject_data["strands"]:
        strand_name = strand_data["name"]
        
        # Check if strand exists
        existing_strand = await db.strands.find_one({
            "name": strand_name,
            "subjectId": subject_id
        })
        
        if existing_strand:
            strand_id = str(existing_strand["_id"])
            print(f"    [EXISTS] Strand: {strand_name}")
        else:
            result = await db.strands.insert_one({
                "name": strand_name,
                "subjectId": subject_id
            })
            strand_id = str(result.inserted_id)
            strands_count += 1
            print(f"    [CREATE] Strand: {strand_name}")
        
        # Process substrands
        for substrand_data in strand_data["substrands"]:
            substrand_name = substrand_data["name"]
            
            # Check if substrand exists
            existing_substrand = await db.substrands.find_one({
                "name": substrand_name,
                "strandId": strand_id
            })
            
            if existing_substrand:
                substrand_id = str(existing_substrand["_id"])
                print(f"      [EXISTS] Substrand: {substrand_name}")
            else:
                result = await db.substrands.insert_one({
                    "name": substrand_name,
                    "strandId": strand_id
                })
                substrand_id = str(result.inserted_id)
                substrands_count += 1
                print(f"      [CREATE] Substrand: {substrand_name}")
            
            # Process SLOs
            for slo_data in substrand_data["slos"]:
                existing_slo = await db.slos.find_one({
                    "name": slo_data["name"],
                    "substrandId": substrand_id
                })
                
                if not existing_slo:
                    await db.slos.insert_one({
                        "name": slo_data["name"],
                        "description": slo_data["description"],
                        "substrandId": substrand_id
                    })
                    slos_count += 1
    
    print(f"\n  Summary for {subject_name}:")
    print(f"    - Strands added: {strands_count}")
    print(f"    - Substrands added: {substrands_count}")
    print(f"    - SLOs added: {slos_count}")
    
    return strands_count, substrands_count, slos_count


async def main():
    """Main function to seed all subjects"""
    print("=" * 70)
    print("SEEDING 5 NEW SUBJECTS FROM KICD CURRICULUM PDFs")
    print("=" * 70)
    
    total_strands = 0
    total_substrands = 0
    total_slos = 0
    
    for subject_name, subject_data in ALL_SUBJECTS.items():
        strands, substrands, slos = await seed_subject(subject_name, subject_data)
        total_strands += strands
        total_substrands += substrands
        total_slos += slos
    
    print("\n" + "=" * 70)
    print("SEEDING COMPLETE")
    print("=" * 70)
    print(f"Total Strands Added: {total_strands}")
    print(f"Total Substrands Added: {total_substrands}")
    print(f"Total SLOs Added: {total_slos}")
    
    # Verify totals
    subjects_count = await db.subjects.count_documents({})
    strands_count = await db.strands.count_documents({})
    substrands_count = await db.substrands.count_documents({})
    slos_count = await db.slos.count_documents({})
    
    print(f"\nDatabase Totals:")
    print(f"  Subjects: {subjects_count}")
    print(f"  Strands: {strands_count}")
    print(f"  Substrands: {substrands_count}")
    print(f"  SLOs: {slos_count}")


if __name__ == "__main__":
    asyncio.run(main())
