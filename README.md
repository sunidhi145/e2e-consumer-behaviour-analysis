# e2e-consumer-behaviour-analysis
This project focuses on analyzing retail banking customer behaviour to identify meaningful customer groups based on how they use banking products and services.
The core problem statement was that banks often hold large volumes of customer data, but without segmentation it is difficult to personalize engagement, improve retention, or design targeted offers.
The goal of the project was to build an end-to-end data and analytics solution that transforms raw banking data into actionable customer segments.
The project uses a realistic retail banking dataset containing customer, account, balance, transaction, and product information.
The first stage of the solution was data preprocessing and transformation using dbt and Snowflake.
Raw data was loaded into Snowflake and organized through a layered dbt pipeline using RAW, VALIDATED, CLEANSED, INTERMEDIATE, and MART schemas.
In the validated layer, data types such as dates, timestamps, and numeric values were standardized to create a reliable base.
In the cleansed layer, duplicate records, inconsistent category values, mixed date formats, and unnecessary fields were handled to improve data quality.
In the intermediate layer, reusable business logic was built to calculate customer-level behavioural metrics.
These engineered features included measures such as average monthly balance, transaction frequency, recency, average transaction value, active months ratio, product depth, and digital channel usage.
The final mart layer produced a machine-learning-ready feature table with one row per customer and no null feature values.
The second stage of the project focused on unsupervised machine learning using K-means clustering.
K-means was selected because the problem did not have predefined customer labels, and the objective was to discover natural behavioural groupings in the data.
The engineered features were scaled and used to train the clustering model, and an appropriate number of clusters was chosen through evaluation techniques such as the elbow method and cluster interpretation.
The resulting clusters represented distinct customer behaviour patterns such as high-value customers, active spenders, digitally engaged users, young savers, and dormant customers.
The third stage of the project was the development of a web application dashboard to make the results easy to explore and explain.
The dashboard allows users to view customer segments, compare cluster characteristics, and understand the behavioural drivers behind each group.
This makes the solution useful not only from a technical point of view, but also for business teams working on customer strategy, marketing, and relationship management.
Overall, the project demonstrates an end-to-end workflow covering data engineering, feature engineering, machine learning, and business-facing analytics delivery.
In summary, this project turns raw retail banking data into clear customer insights that can support smarter segmentation, better decision-making, and more personalized banking experiences.
