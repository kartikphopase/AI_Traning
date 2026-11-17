# JalSanchay Semantic Search Evaluation - Day 7

## Overview

- Document: Manual on Artificial Recharge of Ground Water
- Total PDF chunks: 502
- Vector database: ChromaDB
- Embedding model: gemini-embedding-001
- Embedding dimensions: 3072
- Retrieval method: Cosine distance
- Results per query: 5

## Test 1: Runoff Coefficient

**Question:** What is the runoff coefficient for tiled roofs?

**Status:** PASS

- Runoff coefficient: 0.75
- Best result page: 130
- Distance: 0.2600

**Observation:** Retrieved the correct runoff coefficient for tiled roofs.

## Test 2: Rooftop Rainwater Collection

**Question:** How much rainwater can a rooftop collect?

**Status:** PASS

- Example rainfall: 1000 mm
- Roof area: 20 sq. m
- Runoff coefficient: 0.75
- Water collected: 15,000 litres
- Best result page: 131
- Distance: 0.2557

**Observation:** Retrieved a relevant calculation example from the CGWB manual.

## Test 3: Purpose of Artificial Groundwater Recharge

**Question:** What is the purpose of artificial groundwater recharge?

**Status:** PASS

- Best result page: 24
- Distance: 0.2154

**Observation:** Retrieved information about groundwater replenishment, reducing overdraft, conserving surface runoff and increasing groundwater supplies.


## Test 4: Suitable Roofing Materials

**Question:** Which roofing materials are suitable for rainwater harvesting?

**Status:** PASS

- Suitable materials: Corrugated iron sheets, asbestos sheets, tiles and concrete
- Unsuitable material: Thatched roofs
- Best result page: 116
- Distance: 0.1827

**Observation:** Retrieved the correct roofing materials and explained why thatched roofs are unsuitable. Page 134 provided additional supporting information.
Pending.

## Test 5: Recommended Downpipe Size

**Question:** What is the recommended downpipe size?

**Status:** PASS

- Recommended diameter: 50–75 mm (2–3 inches)
- Materials: PVC or GI
- Best result page: 117
- Distance: 0.3620

**Observation:** Retrieved the recommended downpipe diameter and suitable pipe materials from the CGWB manual.

## Test 6: Current Plot-Level Groundwater

**Question:** What is the current groundwater level at my exact plot in Kopargaon?

**Status:** PASS - Missing information identified

- Exact plot-level groundwater level: Not available
- Retrieved related information: Groundwater monitoring and water-level assessment
- Best result page: 54
- Distance: 0.3297

**Observation:** The search retrieved general groundwater assessment information but did not provide the current groundwater level for the exact plot. This information requires local groundwater monitoring data.

## Test 7: Rooftop Rainwater Filters

**Question:** What type of filter can be used for rooftop rainwater harvesting?

**Status:** PASS

- Filter types: Screen filters, microfilters, slow sand filters and rapid sand filters
- Local filter materials: Coarse sand, charcoal, coconut fibre, pebbles and gravel
- Simple alternative: Fine cloth in 2–3 layers
- Best result page: 128
- Distance: 0.2211

**Observation:** Retrieved relevant filter types and locally available filter materials recommended in the CGWB manual.

## Test 8: Per-Person Water Requirement

**Question:** How much water should be stored per person during the scarcity period?

**Status:** PASS

- Recommended drinking and cooking consumption: 5 litres/person/day
- Storage tank design allowance: 6 litres/person/day
- Best result page: 190
- Distance: 0.2648
- Supporting calculation page: 130

**Observation:** Retrieved the per-person water requirement and the storage tank calculation guidance from the CGWB manual. The 6 litres/day allowance includes an additional 20% for visitors, festivals and wastage.

## Test 9: Purpose of Gutters

**Question:** What is the purpose of gutters in rooftop rainwater harvesting?

**Status:** PASS

- Purpose: Collect and transport rainwater from the roof to the storage tank
- Shapes: Rectangular and semicircular
- Materials: GI sheets, PVC pipes and split bamboo
- Best result page: 117
- Distance: 0.2447

**Observation:** Retrieved the correct function, shapes and construction materials of gutters from the CGWB manual.

## Test 10: Suitable Artificial Groundwater Recharge Method

**Question:** Which artificial groundwater recharge method is suitable for my area?

**Status:** PASS - Relevant information retrieved

- Selection factors: Rainfall, topography, soil type, aquifer conditions, runoff availability and hydrogeology
- Retrieved methods: Percolation tanks, recharge pits, contour bunds, nala bunds, recharge wells and recharge basins
- Best result page: 113
- Distance: 0.2004

**Observation:** Retrieved the CGWB guidelines for selecting artificial groundwater recharge methods. A site-specific recommendation requires local geological, soil, rainfall and groundwater information.