# 🎬 AI-Powered Livestream Writer

An intelligent Python application that helps create engaging livestream content by scraping product information, generating scripts, and responding to comments automatically.

## 🚀 Features

### 🔍 Product Scraping Module
- Live online search
- Static input

### 📝 Script Generation Module
- Generate script based on product scraping results

### 💬 Comment Responder Module
- Answer live questions based on product scraping results

#### Prompt Dev Logs
##### Version 1
##### scraper

Given this provided product introduction {product}, please give me a more detailed introduction about this product.

If there are any real user review, extract it. Otherwise predict potential product reviews and user feedback 
based on the original product description {product} and early generated product details {product_details}.
Focus on actual user experiences, ratings, and opinions.

please analyze the sentiment based on the product details {input}.

##### scripts

Given the following product details {product_details}, pros and cons {product_pros_cons}, sentiment analysis {product_sentiment},
Generate a {time} long introduction script to describe this product, attract more target users, make the context fun and appealing. 
Give me script only.

##### responder

Given the following product details {product_details}, pros and cons {product_pros_cons}, sentiment analysis {product_sentiment},
answer the question {question} based on the above information. Generate a {time} long answer, attract more target users, make the context fun and appealing. 
Don't repeat on the same information in product details.
Give me script only.

##### Version 2
##### scraper

Given this provided product introduction {product}, please give me a detailed, as thorough as possible summary of all features about this product. If there are any real customer reviews in the content, please also extract the real product introduction from the reviews. Please also make sure the results are accurate.

if there are any real user reviews, extract it and make sure they are accurate. Otherwise predict potential product reviews and user feedback 
based on the original product description and early generated product details {product_details}.
Focus on actual user experiences, ratings, and opinions. Be thorough. 

please analyze the sentiment based on the product details and reviews {input}.

##### scripts

You are trying to sell this product through live stream. Give an opening introduction for this product. The targets are to attract more target users, make the live stream fun and appealing.
You have the product details {product_details}, real customer reviews and pros and cons {product_pros_cons}, sentiment analysis {product_sentiment},
Generate a {time} long introduction script to describe this product. Please note the actual live stream contains product introduction, audience comments addressing, so don't make the intro sounds like something you can only say once
Give me script only.

##### responder

Given the following product details {product_details}, pros and cons {product_pros_cons}, sentiment analysis {product_sentiment},
answer the question {question} based on the above information. Generate a {time} long answer, attract more target users, make the context fun and appealing. 
Don't repeat on the same information in product details.
Give me script only.