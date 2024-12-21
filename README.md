# Predicting Ship Arrival Times at Saqr Port

An analysis project examining the quality and temporal reliability of AIS data for predicting ship arrivals at Saqr Port in Ras Al Khaimah (RAK), UAE.

## Overview

This project analyzes Automatic Identification System (AIS) data to improve the prediction accuracy of ship arrivals at Saqr Port. The research aims to enhance operational efficiency and reduce demurrage costs through better arrival time forecasting.

## Key Components

- Data analysis of 23,626 AIS records (2.18GB) from 904 unique vessels
- Implementation of four regression models:
  - Linear Regression (single variable)
  - Multiple Linear Regression
  - Regression Decision Tree
  - Random Forest

## Findings

- Random Forest and Regression Tree models outperformed linear regression approaches
- Arrival prediction accuracy varies significantly by day of the week
- Ship-specific patterns significantly influence prediction quality
- Multiple variables improve prediction accuracy

## Recommendations

- Integrate weather pattern data
- Segment ships based on seasonal patterns
- Optimize port operations personnel based on predictions
- Plan for future port capacity considering RAK's growth