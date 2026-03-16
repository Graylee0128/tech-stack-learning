# Chapter 4: Heating- and Cooling-Load Calculations

---

## 4-1 Introduction

Buildings are built to provide a safe and comfortable internal environment despite variations in external conditions. The extent to which the desired interior conditions can be economically maintained is one important measure of the success of a building design. Although control of inside conditions is usually attributed to the active heating and cooling system, the design of heating, ventilating, and air conditioning (HVAC) must start with an examination of the thermal characteristics of the envelope. They influence both the equipment capacity and the energy required for its operation.

The primary intent of this chapter is to examine procedures for evaluating the impact of the thermal characteristics of the building envelope on the design of the HVAC systems used to maintain comfort. As the objective of the system is to provide comfort, however, it is advisable to begin with a brief discussion of the factors which influence comfort.

---

## 4-2 Health and Comfort Criteria

The human body is an amazingly adaptable organism. With long-term conditioning the body can function under quite extreme thermal conditions. Variations in outdoor temperature and humidity, however, often go beyond the normal limits of adaptability, and it becomes necessary to provide modified conditions indoors in order to maintain a healthy, comfortable environment.

---

## 4-3 Thermal Comfort

> *[Figure 4-1] Factors influencing thermal comfort.*

Four factors influence thermal comfort: metabolic heat generation, clothing insulation, environmental conditions, and physiological factors (age, health, activity level).

The body is continuously generating heat, which must be dissipated to maintain a constant body temperature. The various mechanisms by which temperature control is accomplished were described in Sec. 2-19 and are shown in Fig. 4-1. For a person at rest or doing light work in a conditioned space, the body dissipates heat primarily by convection (carried away by the surrounding air) and radiation (to surrounding surfaces that are at a lower temperature than the body surface). Each of these components of heat dissipation accounts for approximately 30 percent of the heat loss. Evaporation, from both respiration and perspiration, accounts for the remaining 40 percent. As environmental conditions or levels of activity change, these percentages will vary. For example, if a person is doing strenuous work, the primary heat-dissipation mechanism will be evaporation.

Four environmental factors influence the body's ability to dissipate heat: air temperature, the temperature of the surrounding surfaces, humidity, and air velocity. The amount and type of clothing and the activity levels of the occupants interact with these factors. In designing an air-conditioning system we turn our attention to the control of these four factors. If a person is wearing appropriate clothing, the following ranges should usually be acceptable:

- **Operative temperature**: 20 to 26°C
- **Humidity**: A dew-point temperature of 2 to 17°C
- **Average air velocity**: Up to 0.25 m/s

The operative temperature is approximately the average of the air dry-bulb temperature and the mean radiant temperature as long as the mean radiant temperature is less than 50°C and the average air velocity is less than 0.4 m/s. The mean radiant temperature is the uniform surface temperature of an imaginary black enclosure with which an occupant would have the same radiant energy exchange as in the actual nonuniform space. A person wearing heavy clothing may be comfortable at lower temperatures; conversely, lighter clothing and higher air velocity may provide comfort despite higher temperatures. The temperatures of surrounding surfaces have an influence on comfort as great as that of the air temperature and cannot be neglected.

---

## 4-4 Air Quality

Air quality must also be maintained to provide a healthy, comfortable indoor environment. Sources of pollution exist in both the internal and external environment. Indoor air quality is controlled by removal of the contaminant or by dilution. Ventilation plays an important role in both processes. Ventilation is defined as supplying air by natural or mechanical means to a space. Normally, ventilation air is made up of outdoor air and recirculated air. The outdoor air is provided for dilution. In most cases odor and irritation of the upper respiratory tract or eyes are the reason for ventilation rather than the presence of health-threatening contaminants. The possibility of contaminants cannot be overlooked, however.

Reference 2 prescribes both necessary quantities of ventilation for various types of occupancies and methods of determining the proportions of outside air and recirculated air. If the level of contaminants in outdoor air exceeds that for minimum air-quality standards, extraordinary measures beyond the scope of this text must be used. For the present discussion it will be presumed that outdoor-air quality is satisfactory for dilution purposes.

**Table 4-1 Outdoor-air requirements for ventilation**

| Function | Estimated occupancy per 100 m² floor area | Outdoor-air requirements per person, L/s (Smoking) | Outdoor-air requirements per person, L/s (Nonsmoking) |
|---|---|---|---|
| Offices | 7 | 10 | 2.5 |
| Meeting and waiting spaces | 60 | 17.5 | 3.5 |
| Lobbies | 30 | 7.5 | 2.5 |

Much larger quantities of air are required for dilution in areas where smoking is permitted. Ventilation imposes a significant load on heating and cooling equipment and thus is a major contribution to energy use.

The ASHRAE Standard provides the following procedure for determining the allowable rate for recirculation:

$$\dot{V} = \dot{V}_r + \dot{V}_m$$

where:
- $\dot{V}$ = rate of supply air for ventilation purposes, L/s
- $\dot{V}_r$ = recirculation air rate, L/s
- $\dot{V}_m$ = minimum outdoor-air rate for specified occupancy, but never less than 2.5 L/s per person

Also:

$$\dot{V}_r = \frac{\dot{V}_o - \dot{V}_m}{E}$$

where:
- $\dot{V}_o$ = outdoor-air rate from Table 4-1 for specified occupancy (smoking or nonsmoking, as appropriate), L/s
- $E$ = efficiency of contaminant removal by air-cleaning device

**Table 4-2 ASHRAE dust spot efficiencies (1-μm particles)**

| Filter type | Efficiency range, % | Application |
|---|---|---|
| Viscous impingement | 5–25 | Dust and lint removal |
| Dry media: Glass fiber, multi-ply cellulose, wool felt | 25–40 | Same as above and for some industrial applications |
| Mats of 3- to 10-μm fiber, 6 to 20 mm thick | 40–80 | Building recirculated- and fresh-air systems |
| Mats of 0.5- to 4-μm fiber (usually glass) | 80–98 | Hospital surgeries, clean rooms, special applications |
| Electrostatic (depending on type) | 20–90 | Pollen and airborne particles |

**Example 4-1** Determine the ventilation rate, outdoor-air rate, and recirculated-air rate for an office-building meeting room if smoking is permitted. An air-cleaning device with $E$ = 60 percent for removal of tobacco smoke is available.

*Solution* Table 4-1 indicates that 17.5 L/s of outdoor air per person would be required to ventilate the space without any recirculation and air cleaning. The table also indicates that 3.5 L/s per person is the required outdoor-air rate for nonsmoking spaces and may be assumed to be the minimum rate. There are two possible solutions: (a) supply 17.5 L/s of outdoor air per person or (b) calculate the allowable recirculation rate:

$$\dot{V}_r = \frac{\dot{V}_o - \dot{V}_m}{E} = \frac{17.5 - 3.5}{60/100} = 23.3 \text{ L/s}$$

Then $\dot{V} = 23.3 + 3.5 = 26.8$ L/s per person.

Although the total ventilation rate is higher for the second approach, the energy requirements may be less due to the reduced outside-air flow rate.

If contamination is the result of occupancy, ventilation is not required when the space is not occupied. If other sources of contamination exist (equipment, processes, outgassing from materials, radon), an appropriate level of ventilation must be maintained even if the space is unoccupied.

---

## 4-5 Estimating Heat Loss and Heat Gain

Heat transfer through a building envelope is influenced by the materials used; by geometric factors such as size, shape, and orientation; by the existence of internal heat sources; and by climatic factors. System design requires each of these factors to be examined and the impact of their interactions to be carefully evaluated.

The primary function of heat-loss and heat-gain calculations is to estimate the capacity that will be required for the various heating and air-conditioning components necessary to maintain comfort within a space. These calculations are therefore based on peak-load conditions for heating and cooling and correspond to environmental conditions which are near the extremes normally encountered.

Loads are generally divided into the following four categories (*Figure 4-2*):

> *[Figure 4-2] Categories of heating and cooling loads.*

- **Transmission**: Heat loss or heat gain due to a temperature difference across a building element
- **Solar**: Heat gain due to transmission of solar energy through a transparent building component or absorption by an opaque building component
- **Infiltration**: Heat loss or heat gain due to the infiltration of outside air into a conditioned space
- **Internal**: Heat gain due to the release of energy within a space (lights, people, equipment, etc.)

In response to these loads the temperature in the space will change or the heating or cooling equipment will operate to maintain a desired temperature.

---

## 4-6 Design Conditions

The design conditions usually specified for estimating heating loads are the inside and outside dry-bulb temperatures. For heating operation an indoor temperature of 20 to 22°C is generally assumed, and for cooling operation 24 to 26°C is typical. A minimum relative humidity of 30% in the winter and a maximum of 60% in the summer is also assumed. For heating operation the 97.5 percent value of the outside temperature is usually chosen. This means that on a long-term basis the outside dry-bulb temperature equals or exceeds this value for 97.5 percent of the hours during the coldest months of the year. At the 97.5 percent outdoor temperature the air is assumed to be saturated.

The set of conditions specified for cooling-load estimates is more complex and includes dry-bulb temperature, humidity, and solar intensity. Peak-load conditions during the cooling season usually correspond to the maximum solar conditions rather than to the peak outdoor-air temperature. Thus, it is often necessary to make several calculations at different times of the day or times of the year to fix the appropriate maximum-cooling-capacity requirements.

**Table 4-3 Design temperature data**

| City | Winter 97.5% dry bulb, °C | Summer 2.5% dry bulb / coincident wet bulb, °C | August daily average, °C |
|---|---|---|---|
| Albuquerque, N. Mex. | -9 | 33/16 | 24 |
| Atlanta, Ga. | -6 | 33/23 | 26 |
| Boise, Idaho | -12 | 34/18 | 22 |
| Boston, Mass. | -13 | 31/22 | 22 |
| Chicago, Ill. | -18 | 33/23 | 23 |
| Columbus, Ohio | -15 | 32/23 | 23 |
| Dallas, Tex. | -6 | 36/24 | 29 |
| Denver, Colo. | -17 | 33/15 | 22 |
| El Paso, Tex. | -5 | 37/18 | 27 |
| Great Falls, Mont. | -26 | 31/16 | 19 |
| Houston, Tex. | 0 | 34/25 | 28 |
| Las Vegas, Nev. | -2 | 41/18 | 31 |
| Los Angeles, Calif. | 4 | 32/21 | 21 |
| Memphis, Tenn. | -8 | 35/24 | 27 |
| Miami, Fla. | 8 | 32/25 | 28 |
| Minneapolis, Minn. | -24 | 37/23 | 22 |
| New Orleans, La. | -4 | 33/26 | 28 |
| New York, N.Y. | -9 | 32/23 | 24 |
| Phoenix, Ariz. | 1 | 42/22 | 32 |
| Pittsburgh, Pa. | -14 | 31/22 | 22 |
| Portland, Oreg. | -4 | 30/20 | 20 |
| Sacramento, Calif. | 0 | 37/21 | 26 |
| Salt Lake City, Utah | -13 | 35/17 | 24 |
| San Francisco, Calif. | 4 | 22/17 | 17 |
| Seattle, Wash. | -3 | 28/19 | 18 |
| Spokane, Wash. | -17 | 32/17 | 20 |
| St. Louis, Mo. | -13 | 34/24 | 25 |
| Washington, D.C. | -8 | 33/23 | 25 |

The 2.5 percent dry-bulb temperature is the temperature exceeded by 2.5 percent of the hours during June to September. The mean coincident wet-bulb temperature is the mean wet-bulb temperature occurring at that 2.5 percent dry-bulb temperature.

**Example 4-2** Select outside and inside design temperatures for a building to be constructed in Denver, Colorado.

*Solution* From Table 4-3:
- Summer design dry-bulb temperature = 33°C
- Coincident wet-bulb temperature = 15°C
- Inside design: 25°C, 60% relative humidity

Winter design:
- Outside temperature = -17°C (from Table 4-3)
- Inside design: 20°C, 30% relative humidity

It should be noted that the inside design temperature only limits the conditions that can be maintained in extreme weather.

---

## 4-7 Thermal Transmission

The general procedure for calculating heat loss or heat gain by thermal transmission is to apply Eq. (2-12):

$$q = \frac{A \Delta t}{R_{tot}} = UA(t_o - t_i)$$

where:
- $UA = 1/R_{tot}$, W/K
- $R_{tot}$ = total thermal resistance, K/W
- $U$ = overall heat-transfer coefficient, W/m² · K
- $A$ = surface area, m²
- $t_o - t_i$ = outside-inside temperature difference, K

For heating-load estimates the temperature difference is simply the 97.5 percent outside value minus the inside design value.

**Table 4-4 Thermal resistance of unit areas of selected building materials at 24°C mean temperature**

*Exterior material:*

| Material | 1/k, m · K/W | R, m² · K/W |
|---|---|---|
| Face brick | 0.76 | |
| Common brick | 1.39 | |
| Stone | 0.55 | |
| Concrete block, sand and gravel aggregate, 200 mm | | 0.18 |
| Lightweight aggregate, 200 mm | | 0.38 |
| Lightweight aggregate, 150 mm | | 0.29 |
| Stucco | 1.39 | |

*Sheathing:*

| Material | 1/k, m · K/W | R, m² · K/W |
|---|---|---|
| Siding, asbestos-cement, 6 mm, lapped | | 0.04 |
| Asphalt insulating, 13 mm | | 0.14 |
| Wood plywood, 10 mm | | 0.10 |
| Aluminum or steel, backed with insulating board, 10 mm | | 0.32 |
| Asbestos-cement | 1.73 | |
| Plywood | 8.66 | |
| Fiberboard, regular density, 13 mm | | 0.23 |
| Hardboard, medium density | 9.49 | |
| Particle board, medium density | 7.35 | |

*Roofing:*

| Material | 1/k, m · K/W | R, m² · K/W |
|---|---|---|
| Asphalt shingles | | 0.08 |
| Built-up roofing, 10 mm | | 0.06 |

*Concrete:*

| Material | 1/k, m · K/W |
|---|---|
| Sand and gravel aggregate | 0.55 |
| Lightweight aggregate | 1.94 |

*Insulating materials:*

| Material | R, m² · K/W |
|---|---|
| Blanket and batt, mineral fiber, 75–90 mm | 1.94 |
| Blanket and batt, mineral fiber, 135–165 mm | 3.35 |
| Board and slab, glass fiber, organic bond | 27.7 (1/k) |
| Expanded polystyrene, extruded | 27.7 (1/k) |
| Cellular polyurethane | 43.8 (1/k) |
| Loose fill, mineral fiber, 160 mm | 3.35 |
| Cellulosic | 21.7–25.6 (1/k) |

*Interior materials:*

| Material | 1/k, m · K/W | R, m² · K/W |
|---|---|---|
| Gypsum or plaster board, 15 mm | | 0.08 |
| Gypsum or plaster board, 16 mm | | 0.10 |
| Cement plaster | 1.39 | |
| Gypsum plaster, lightweight, 16 mm | | 0.066 |
| Wood, soft (fir, pine, etc.) | 8.66 | |
| Hardwood (maple, oak, etc.) | 6.31 | |

*Air resistance:*

| Condition | R, m² · K/W (Summer) | R, m² · K/W (Winter) |
|---|---|---|
| Surface, still air, horizontal, heat flow up | 0.11 | |
| Horizontal, heat flow down | 0.16 | |
| Vertical, heat flow horizontal | 0.12 | |
| Surface, moving air, heating season, 6.7 m/s | | 0.029 |
| Surface, moving air, cooling season, 3.4 m/s | 0.044 | |
| Air space, emissivity 0.8, horizontal | 0.14 | 0.17 |
| Air space, emissivity 0.8, vertical | 0.17 | |
| Air space, emissivity 0.2, horizontal | 0.24 | |
| Air space, emissivity 0.2, vertical | 0.36 | |

*Flat glass (U, W/m² · K):*

| Type | Summer | Winter |
|---|---|---|
| Single glass | 5.9 | 6.2 |
| Double glass, 6-mm air space | 3.5 | 3.3 |
| Double glass, 13-mm air space | 3.2 | 2.8 |
| Triple glass, 6-mm air spaces | 2.5 | 2.2 |
| Triple glass, 13-mm air spaces | 2.2 | 1.8 |
| Storm windows, 25 to 100-mm air space | 2.8 | 2.3 |

> *[Figure 4-3] Wall section in Example 4-3.*

**Example 4-3** Determine the total thermal resistance of a unit area of the wall section shown in Fig. 4-3.

*Solution* The following resistances are obtained from Table 4-4:

| Component | R, m² · K/W |
|---|---|
| Outside air film | 0.029 |
| Face brick, 90 mm | 0.068 |
| Air space | 0.170 |
| Sheathing, 13-mm fiberboard | 0.232 |
| Insulation, 75-mm mineral fiber | 1.940 |
| Air space | 0.170 |
| Gypsum board, 13 mm | 0.080 |
| Inside air film | 0.120 |
| **Total** | **2.809** |

If below-grade spaces are not conditioned, the heat loss through below-grade surfaces is often neglected. If the below-grade spaces are to be conditioned, transmission heat losses are based on the wall and floor thermal resistance, the inside temperature to be maintained, and an estimate of the ground temperature adjacent to the surface.

For slab-on-grade construction the heat loss is more nearly proportional to the length of the perimeter of the slab (in meters) than its area. Thus:

$$q_{slab} = F \times (\text{perimeter}) \times (t_o - t_i)$$

where $F$ = constant. Values for residential-scale slabs: $F$ = 1.4 W/m · K for an uninsulated edge and $F$ = 0.9 W/m · K for a slab with 2.5 cm of insulation at the edge.

---

## 4-8 Infiltration and Ventilation Loads

The entry of outside air into the space influences both the air temperature and the humidity level in the space. Usually a distinction is made between the two effects, referring to the temperature effect as **sensible load** and the humidity effect as **latent load**. This terminology applies to the other load components as well. For example, transmission and solar loads are sensible, as they affect only temperature, while internal loads arising from occupancy have both sensible and latent components.

Heat loss or heat gain due to the entry of outside air is expressed with:
- $\dot{Q}$ = volumetric flow rate of outside air, L/s
- $W$ = humidity ratio, water to air, kg/kg

**Infiltration**, defined as the uncontrolled entry of unconditioned outside air directly into the building, results from natural forces, e.g., wind and buoyancy due to the temperature difference between inside and outside. **Ventilation** is air intentionally brought into the building by mechanical means.

In commercial and institutional buildings it is considered advisable to control the entry of outside air to assure proper ventilation and minimize energy use. These buildings are designed and constructed to limit infiltration by sealing the building envelope, using vestibules or revolving doors, or maintaining a pressure within the building slightly in excess of that outside.

**Table 4-5 Infiltration constants for Eq. (4-1)**

| Quality of construction | a | b | c |
|---|---|---|---|
| Tight | 0.15 | 0.010 | 0.007 |
| Average | 0.20 | 0.015 | 0.014 |
| Loose | 0.25 | 0.020 | 0.022 |

The number of air changes per hour for a smaller building with no internal pressurization can be estimated as:

$$\text{Number of air changes} = a + bV + c(t_o - t_i) \tag{4-1}$$

where:
- $a, b, c$ = experimentally determined constants
- $V$ = wind velocity, m/s

For nonresidential buildings it is customary to use estimates of infiltration for load calculations only when the fans in the ventilation system are not operating.

The slightly positive pressure in the building is maintained by sizing the exhaust fans to handle less air than brought in from the outside by the ventilation system. Exhaust fans are generally located in restrooms, mechanical rooms, or kitchens to ensure that air and odors from these spaces will not be recirculated throughout the building.

Although the outdoor component of ventilation imposes a load on heating and cooling equipment, the load occurs at the point where air is conditioned rather than in the space. It is therefore necessary to distinguish between **equipment loads** and the **space loads** used to determine the airflow required for the building spaces.

---

## 4-9 Summary of Procedure for Estimating Heating Loads

In estimating the heating loads for a building, it is important to use an organized, step-by-step procedure:

1. Select design values for outdoor winter design (97.5 percent value) from Table 4-3.
2. Select an indoor design temperature appropriate to the activities to be carried out in the space and a minimum acceptable relative humidity.
3. Determine whether any special conditions will exist, such as adjacent unconditioned spaces. Estimate temperatures in the unconditioned spaces as necessary.
4. On the basis of building plans and specifications, calculate heat-transfer coefficients and areas for the building components in each enclosing surface. Any surfaces connecting with spaces to be maintained at the same temperature may be omitted, i.e., interior walls.
5. On the basis of building components, system design and operation, wind velocity, and indoor-outdoor temperature difference, estimate the rate of infiltration and/or ventilation outside air. Note that the latent component of the infiltration and/or ventilation load is included only if the conditioned air is to be humidified to maintain a specified minimum indoor humidity level.
6. Using the above design data, compute transmission heat losses for each surface of the building envelope and the heat loss from infiltration and/or ventilation. Sum these values to determine the total estimated heat loss and the required capacity of the heating equipment.
7. Consider any special circumstances that might influence equipment sizing:
   - (a) If a building and its heating system are designed to take advantage of passive solar gain and thermal storage, heating capacities should be based on dynamic rather than static heat-loss analysis (see Chap. 20).
   - (b) In a building that has an appreciable steady internal load (heat release) at the time of the maximum transmission and ventilation heat loss, heating-equipment capacity may be reduced by the amount of the internal heat release.
   - (c) A building that does not operate on a continuous basis and indoor temperatures are allowed to drop over a lengthy unoccupied period — additional capacity may be required to bring the air temperature and building indoor surface temperatures back to an acceptable level in a short time.

---

## 4-10 Components of the Cooling Load

Estimating the cooling load is more complex than estimating the heating load. Additional consideration must be given to internal loads, latent loads, and solar loads.

---

## 4-11 Internal Loads

The primary sources of internal heat gain are lights, occupants, and equipment operating within the space. Internal loads are a major factor in most nonresidential buildings.

### Lighting

The amount of heat gain in the space due to lighting depends on the wattage of the lamps and the type of fixture. When fluorescent lighting is used, the energy dissipated by the ballast must also be included. The radiant energy from the lights is first absorbed by the walls, floor, and furnishings of the space, and their temperatures then increase at a rate dependent on their mass. Thus there is a delay between turning the light on and the energy from the lights having an effect on the load.

$$q = (\text{lamp rating in watts})(F_u)(F_b)(CLF)$$

where:
- $F_u$ = utilization factor or fraction of installed lamps in use
- $F_b$ = ballast factor for fluorescent lamps = 1.2 for most common fluorescent fixtures
- $CLF$ = cooling-load factor from Table 4-6

**Table 4-6 Cooling-load factors for lighting**

| No. of hours after lights are turned on | Fixture X (recessed, not vented) 10h | Fixture X 16h | Fixture Y (vented or free-hanging) 10h | Fixture Y 16h |
|---|---|---|---|---|
| 0 | 0.08 | 0.19 | 0.01 | 0.05 |
| 1 | 0.62 | 0.72 | 0.76 | 0.79 |
| 2 | 0.66 | 0.75 | 0.81 | 0.83 |
| 3 | 0.69 | 0.77 | 0.84 | 0.87 |
| 4 | 0.73 | 0.80 | 0.88 | 0.89 |
| 5 | 0.75 | 0.82 | 0.90 | 0.91 |
| 6 | 0.78 | 0.84 | 0.92 | 0.93 |
| 7 | 0.80 | 0.85 | 0.93 | 0.94 |
| 8 | 0.82 | 0.87 | 0.95 | 0.95 |
| 9 | 0.84 | 0.88 | 0.96 | 0.96 |
| 10 | 0.85 | 0.89 | 0.97 | 0.97 |
| 11 | 0.32 | 0.90 | 0.22 | 0.98 |
| 12 | 0.29 | 0.91 | 0.18 | 0.98 |
| 13 | 0.26 | 0.92 | 0.14 | 0.98 |
| 14 | 0.23 | 0.93 | 0.12 | 0.99 |
| 15 | 0.21 | 0.94 | 0.09 | 0.99 |
| 16 | 0.19 | 0.94 | 0.08 | 0.99 |
| 17 | 0.17 | 0.40 | 0.06 | 0.24 |
| 18 | 0.15 | 0.36 | 0.05 | 0.20 |

> Fixture X: recessed lights which are not vented. Supply and return air registers are below the ceiling or through the ceiling space and grille.
> Fixture Y: vented or free-hanging lights. Supply air registers are below or through the ceiling with the return air registers around the fixtures and through the ceiling space.

### Occupants

**Table 4-7 Heat gain from occupants**

| Activity | Heat gain, W | Sensible heat gain, % |
|---|---|---|
| Sleeping | 70 | 75 |
| Seated, quiet | 100 | 60 |
| Standing | 150 | 50 |
| Walking, 3 km/h | 305 | 35 |
| Office work | 150 | 55 |
| Teaching | 175 | 50 |
| Retail shop | 185 | 50 |
| Industrial | 300–600 | 35 |

**Table 4-8 Space per occupant**

| Type of space | Occupancy |
|---|---|
| Residence | 2–6 occupants |
| Office | 10–15 m² per occupant |
| Retail | 3–5 m² per occupant |
| School | 2.5 m² per occupant |
| Auditorium | 1.0 m² per occupant |

Occupant sensible cooling load in watts:

$$q = (\text{gain per person from Table 4-7}) \times (\text{number of people}) \times (CLF \text{ from Table 4-9})$$

For the latent load the CLF is 1.0.

**Table 4-9 Sensible-heat cooling-load factors for people**

| Hours after each entry into space | Total hours in space: 2 | 4 | 6 | 8 | 10 | 12 | 14 | 16 |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 | 0.49 | 0.50 | 0.51 | 0.53 | 0.55 | 0.58 | 0.62 |
| 2 | 0.58 | 0.59 | 0.60 | 0.61 | 0.62 | 0.64 | 0.66 | 0.70 |
| 3 | 0.17 | 0.66 | 0.67 | 0.67 | 0.69 | 0.70 | 0.72 | 0.75 |
| 4 | 0.13 | 0.71 | 0.72 | 0.72 | 0.74 | 0.15 | 0.77 | 0.79 |
| 5 | 0.10 | 0.27 | 0.76 | 0.76 | 0.77 | 0.79 | 0.80 | 0.82 |
| 6 | 0.08 | 0.21 | 0.79 | 0.80 | 0.80 | 0.81 | 0.83 | 0.85 |
| 7 | 0.07 | 0.16 | 0.34 | 0.82 | 0.83 | 0.84 | 0.85 | 0.87 |
| 8 | 0.06 | 0.14 | 0.26 | 0.84 | 0.85 | 0.86 | 0.87 | 0.88 |
| 9 | 0.05 | 0.11 | 0.21 | 0.38 | 0.87 | 0.88 | 0.89 | 0.90 |
| 10 | 0.04 | 0.10 | 0.18 | 0.30 | 0.89 | 0.89 | 0.90 | 0.91 |
| 11 | 0.04 | 0.08 | 0.15 | 0.25 | 0.42 | 0.91 | 0.91 | 0.92 |
| 12 | 0.03 | 0.07 | 0.13 | 0.21 | 0.34 | 0.92 | 0.92 | 0.93 |
| 13 | 0.03 | 0.06 | 0.11 | 0.18 | 0.28 | 0.45 | 0.93 | 0.94 |
| 14 | 0.02 | 0.06 | 0.10 | 0.15 | 0.23 | 0.36 | 0.94 | 0.95 |
| 15 | 0.02 | 0.05 | 0.08 | 0.13 | 0.20 | 0.30 | 0.47 | 0.95 |
| 16 | 0.02 | 0.04 | 0.07 | 0.12 | 0.17 | 0.25 | 0.38 | 0.96 |
| 17 | 0.02 | 0.04 | 0.06 | 0.10 | 0.15 | 0.21 | 0.31 | 0.49 |
| 18 | 0.01 | 0.03 | 0.06 | 0.09 | 0.13 | 0.19 | 0.26 | 0.39 |

---

## 4-12 Solar Loads through Transparent Surfaces

Heat gain due to solar energy incident on a surface will depend upon the physical characteristics of the surface. Surface optical properties are described by:

$$\tau + \rho + \alpha = 1$$

where:
- $\tau$ = transmittance
- $\rho$ = reflectance
- $\alpha$ = absorptance

> *[Figure 4-4] Distribution of solar heat striking a transparent surface.*

For transparent surfaces, such as windows, the solar energy passing through the surface $q_{sg}$ in watts is:

$$q_{sg} = A(\tau I_t + N\alpha I_t) = AI_t(\tau + N\alpha) \tag{4-2}$$

where:
- $I_t$ = irradiation on exterior surface, W/m²
- $N$ = fraction of absorbed radiation transferred by conduction and convection to inside environment
- $h_o$ = outside heat-transfer coefficient, W/m² · K

Under steady-state conditions $N = U/h_o$. Thus:

$$q_{sg} = AI_t\left(\tau + \frac{U\alpha}{h_o}\right)$$

The expression $I_t(\tau + U\alpha/h_o)$ for a single sheet of clear window glass is frequently referred to as the **solar-heat gain factor (SHGF)**.

**Table 4-10 Maximum solar-heat gain factor for sunlit glass, W/m²**

*32° north latitude:*

| Month | N/shade | NE/NW | E/W | SE/SW | S | Hor. |
|---|---|---|---|---|---|---|
| Dec | 69 | 69 | 510 | 775 | 795 | 500 |
| Jan, Nov | 15 | 90 | 550 | 785 | 115 | 555 |
| Feb, Oct | 85 | 205 | 645 | 780 | 700 | 685 |
| Mar, Sept | 100 | 330 | 695 | 700 | 545 | 780 |
| Apr, Aug | 115 | 450 | 700 | 580 | 355 | 845 |
| May, July | 120 | 530 | 685 | 480 | 230 | 865 |
| June | 140 | 555 | 675 | 440 | 190 | 870 |

*40° north latitude:*

| Month | N/shade | NE/NW | E/W | SE/SW | S | Hor. |
|---|---|---|---|---|---|---|
| Dec | 57 | 51 | 475 | 730 | 800 | 355 |
| Jan, Nov | 63 | 63 | 480 | 155 | 195 | 420 |
| Feb, Oct | 80 | 155 | 575 | 760 | 750 | 565 |
| Mar, Sept | 95 | 285 | 660 | 730 | 640 | 690 |
| Apr, Aug | 110 | 435 | 690 | 630 | 475 | 790 |
| May, July | 120 | 515 | 690 | 545 | 350 | 830 |
| June | 150 | 540 | 680 | 510 | 300 | 840 |

A **shading coefficient (SC)** is used to adjust SHGF values for other types of glass or to account for inside shading devices:

$$SC = \frac{\tau + U\alpha/h_o}{(\tau + U\alpha/h_o)_{ss}}$$

where the subscript *ss* stands for a single sheet of clear glass.

**Table 4-11 Shading coefficients**

| Type of glass | Thickness, mm | No indoor shading | Venetian blinds Medium | Venetian blinds Light | Roller shades Dark | Roller shades Light |
|---|---|---|---|---|---|---|
| **Single glass** | | | | | | |
| Regular sheet | 3 | 1.00 | 0.64 | 0.55 | 0.59 | 0.25 |
| Plate | 6–12 | 0.95 | 0.64 | 0.55 | 0.59 | 0.25 |
| Heat-absorbing | 6 | 0.70 | 0.57 | 0.53 | 0.40 | 0.30 |
| Heat-absorbing | 10 | 0.50 | 0.54 | 0.52 | 0.40 | 0.28 |
| **Double glass** | | | | | | |
| Regular sheet | 3 | 0.90 | 0.57 | 0.51 | 0.60 | 0.25 |
| Plate | 6 | 0.83 | 0.57 | 0.51 | 0.60 | 0.25 |
| Reflective | 6 | 0.2–0.4 | 0.2–0.33 | | | |

The solar energy passing through a window can be expressed as:

$$q_{sg} = (SHGF_{max})(SC)(A)$$

Since solar energy entering the space does not appear instantaneously as a load on the cooling system, a cooling-load factor (CLF) is included:

**Table 4-12 Cooling-load factors for glass with interior shading, north latitudes**

| Solar time, h | N | NE | E | SE | S | SW | W | NW | Hor. |
|---|---|---|---|---|---|---|---|---|---|
| 6 | 0.73 | 0.56 | 0.47 | 0.30 | 0.09 | 0.07 | 0.06 | 0.07 | 0.11 |
| 7 | 0.66 | 0.76 | 0.72 | 0.57 | 0.16 | 0.11 | 0.09 | 0.11 | 0.27 |
| 8 | 0.65 | 0.74 | 0.80 | 0.74 | 0.23 | 0.14 | 0.11 | 0.14 | 0.44 |
| 9 | 0.73 | 0.58 | 0.76 | 0.81 | 0.38 | 0.16 | 0.13 | 0.17 | 0.59 |
| 10 | 0.80 | 0.37 | 0.62 | 0.79 | 0.58 | 0.19 | 0.15 | 0.19 | 0.72 |
| 11 | 0.86 | 0.29 | 0.41 | 0.68 | 0.75 | 0.22 | 0.16 | 0.20 | 0.81 |
| 12 | 0.89 | 0.27 | 0.27 | 0.49 | 0.83 | 0.38 | 0.17 | 0.21 | 0.85 |
| 13 | 0.89 | 0.26 | 0.24 | 0.33 | 0.80 | 0.59 | 0.31 | 0.22 | 0.85 |
| 14 | 0.86 | 0.24 | 0.22 | 0.28 | 0.68 | 0.75 | 0.53 | 0.30 | 0.81 |
| 15 | 0.82 | 0.22 | 0.20 | 0.25 | 0.50 | 0.83 | 0.72 | 0.52 | 0.71 |
| 16 | 0.75 | 0.20 | 0.17 | 0.22 | 0.35 | 0.81 | 0.82 | 0.73 | 0.58 |
| 17 | 0.78 | 0.16 | 0.14 | 0.18 | 0.27 | 0.69 | 0.81 | 0.82 | 0.42 |
| 18 | 0.91 | 0.12 | 0.11 | 0.13 | 0.19 | 0.45 | 0.61 | 0.69 | 0.25 |

### External Shading

> *[Figure 4-5] Shading angles and dimensions.*

When estimating solar-heat gain through transparent surfaces, external shading must be considered. The depth of a shadow below a horizontal projection of width $d$ is given by:

$$y = d \frac{\tan \beta}{\cos \gamma}$$

The width of a shadow cast by a vertical projection of depth $d$ is:

$$x = d \tan \gamma$$

where:
- $\beta$ = solar altitude angle (angle from horizontal plane up to the sun)
- $\gamma$ = wall-azimuth angle (angle between two vertical planes, one normal to the wall and the other containing the sun)

The wall-azimuth angle:

$$\gamma = \phi \pm \psi$$

where $\psi$ is the angle a vertical plane normal to the wall makes with the south.

**Table 4-13 Solar position angles for the twenty-first day of month**

*32° north latitude:*

| Month | Angle | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|
| Dec | β | | | 10 | 20 | 28 | 33 | 35 | |
| | φ | | | 54 | 44 | 31 | 16 | 0 | |
| Jan, Nov | β | | 1 | 13 | 22 | 31 | 36 | 38 | |
| | φ | | 65 | 56 | 46 | 33 | 18 | 0 | |
| Feb, Oct | β | | 7 | 18 | 29 | 38 | 45 | 47 | |
| | φ | | 73 | 64 | 53 | 39 | 21 | 0 | |
| Mar, Sep | β | | 13 | 25 | 37 | 47 | 55 | 58 | |
| | φ | | 82 | 73 | 62 | 47 | 27 | 0 | |
| Apr, Aug | β | 6 | 19 | 31 | 44 | 56 | 65 | 70 | |
| | φ | 100 | 92 | 84 | 74 | 60 | 37 | 0 | |
| May, Jul | β | 10 | 23 | 35 | 48 | 61 | 72 | 78 | |
| | φ | 107 | 100 | 93 | 85 | 73 | 52 | 0 | |
| Jun | β | 1 | 12 | 24 | 37 | 50 | 62 | 74 | 81 |
| | φ | 118 | 110 | 103 | 97 | 89 | 80 | 61 | 0 |

*40° north latitude:*

| Month | Angle | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|
| Dec | β | | | 5 | 14 | 21 | 25 | 27 | |
| | φ | | | 53 | 42 | 29 | 15 | 0 | |
| Jan, Nov | β | | | 8 | 17 | 24 | 28 | 30 | |
| | φ | | | 55 | 44 | 31 | 16 | 0 | |
| Feb, Oct | β | | 4 | 15 | 24 | 32 | 37 | 39 | |
| | φ | | 72 | 62 | 50 | 35 | 19 | 0 | |
| Mar, Sep | β | | 11 | 23 | 33 | 42 | 48 | 50 | |
| | φ | | 80 | 70 | 57 | 42 | 23 | 0 | |
| Apr, Aug | β | 7 | 19 | 30 | 41 | 51 | 59 | 62 | |
| | φ | 99 | 89 | 79 | 67 | 51 | 29 | 0 | |
| May, Jul | β | 2 | 13 | 24 | 35 | 47 | 51 | 66 | 70 |
| | φ | 115 | 106 | 97 | 87 | 76 | 61 | 37 | 0 |
| Jun | β | 4 | 15 | 26 | 37 | 49 | 60 | 69 | 73 |
| | φ | 117 | 108 | 100 | 91 | 80 | 66 | 42 | 0 |

> Note: Solar time P.M. values are symmetric — use same β values; φ values read from right to left (12, 1, 2, ... maps to columns 12, 11, 10, ...).

**Example 4-4** A 1.25-m high by 2.5-m wide window is inset from the face of the wall 0.15 m. Calculate the shading provided by the inset at 2 P.M. sun time if the window is facing south at 32° north latitude, August 21.

*Solution* For a south-facing window, $\psi = 0$ and $\gamma = \phi$. From Table 4-13, $\beta = 56°$ and $\gamma = 60°$; then:

$$x = d \tan \gamma = 0.15 \tan 60° = 0.26 \text{ m}$$

$$y = d \frac{\tan \beta}{\cos \gamma} = \frac{0.15 \tan 56°}{\cos 60°} = 0.44 \text{ m}$$

Sunlit area = $(2.5 - 0.26)(1.25 - 0.44) = 1.81$ m²

---

## 4-13 Solar Loads on Opaque Surfaces

> *[Figure 4-6] Solar loads on opaque surfaces.*

A portion of the solar energy is reflected and the remainder absorbed. Of the energy absorbed some is convected and some reradiated to the outside. The remainder of the absorbed solar energy is transmitted to the inside by conduction or temporarily stored.

The transmissivity $\tau$ of an opaque surface is zero, thus $\rho + \alpha = 1$, and Eq. (4-2) reduces to:

$$q_w = \frac{U_w \alpha}{h_o} I_t A$$

If the transmission due to the air-temperature difference is included:

$$q = \frac{U_w \alpha}{h_o} I_t A + U_w A(t_o - t_i) \tag{4-3}$$

Rearranging:

$$q = U_w A \left[\left(t_o + \frac{\alpha I_t}{h_o}\right) - t_i\right] \tag{4-4}$$

If the first term in the brackets is replaced by an equivalent temperature $t_e$ (the **sol-air temperature**):

$$t_e = t_o + \frac{\alpha I_t}{h_o}$$

Then:

$$q = U_w A(t_e - t_i)$$

The sol-air temperature is the outdoor temperature increased by an amount to account for the solar radiation.

### Cooling-Load Temperature Difference (CLTD)

For opaque walls, the effects of thermal storage can be quite pronounced. To incorporate the effect of thermal storage, the **cooling-load temperature difference (CLTD)** has been developed for commonly used wall cross sections. It takes into account both the solar flux on the surface and the thermal capacitance of the mass of the wall.

$$q_w = UA(CLTD) \tag{4-5}$$

> *[Figure 4-7] Heat flux through two walls with the same U values but different masses.*

**Table 4-14 Cooling-load temperature difference for flat roofs, K**

*Roofs without suspended ceilings:*

| Roof type | kg/m² | kJ/m²·K | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 35 | 45 | 3 | 11 | 19 | 27 | 34 | 40 | 43 | 44 | 43 | 39 | 33 | 25 | 17 | 10 |
| 2 | 40 | 75 | -1 | 2 | 8 | 15 | 22 | 29 | 35 | 39 | 41 | 41 | 39 | 34 | 29 | 21 |
| 3 | 90 | 90 | -2 | 1 | 5 | 11 | 18 | 25 | 31 | 36 | 39 | 40 | 40 | 37 | 32 | 25 |
| 4 | 150 | 120 | 1 | 0 | 2 | 4 | 8 | 13 | 18 | 24 | 29 | 33 | 35 | 36 | 35 | 32 |
| 5 | 250 | 230 | 4 | 4 | 6 | 8 | 11 | 15 | 18 | 22 | 25 | 28 | 29 | 30 | 29 | 27 |
| 6 | 365 | 330 | 9 | 8 | 7 | 8 | 8 | 10 | 12 | 15 | 18 | 20 | 22 | 24 | 25 | 26 |

*Roofs with suspended ceilings:*

| Roof type | kg/m² | kJ/m²·K | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 45 | 50 | 0 | 5 | 13 | 20 | 28 | 35 | 40 | 43 | 43 | 41 | 37 | 31 | 23 | 15 |
| 2 | 50 | 85 | 1 | 2 | 4 | 7 | 12 | 17 | 22 | 27 | 31 | 33 | 35 | 34 | 32 | 28 |
| 3 | 100 | 100 | 0 | 0 | 2 | 6 | 10 | 16 | 21 | 27 | 31 | 34 | 36 | 36 | 34 | 30 |
| 4 | 150 | 130 | 6 | 4 | 4 | 4 | 6 | 9 | 12 | 16 | 20 | 24 | 27 | 29 | 30 | 30 |
| 5 | 260 | 240 | 12 | 11 | 11 | 11 | 12 | 13 | 15 | 16 | 18 | 19 | 20 | 21 | 21 | 21 |
| 6 | 360 | 340 | 13 | 13 | 13 | 12 | 12 | 13 | 13 | 14 | 15 | 16 | 16 | 17 | 18 | 18 |

> *Notes:*
> 1. Directly applicable for: inside temperature = 25°C; outside temperature, maximum = 35°C, average = 29°C; daily range = 12°C; solar radiation typical of July 21 at 40° north latitude.
> 2. Adjustments: $CLTD_{adj} = CLTD + (25 - t_i) + (t_{av} - 29)$ where $t_i$ = inside design dry-bulb temperature, $t_{av}$ = average outdoor dry-bulb temperature for design day.
> 3. For roof constructions not listed, choose the roof from the table which is of approximately the same density and heat capacity.
> 4. When the roof has additional insulation, for each $R = 1.2$ m²·K/W in additional insulation use the CLTD for the next thermally heavier roof.
>
> Roof types: 1 = Sheet steel with 25 to 50 mm insulation, 2 = 25 mm wood with 25 mm insulation, 3 = 100 mm lightweight concrete, 4 = 150 mm lightweight concrete, 5 = 100 mm heavyweight concrete, 6 = roof terrace system.

**Table 4-15 Cooling-load temperature difference for sunlit walls**

*Wall type G (metal curtain or frame wall with 25–75 mm insulation), 50 kg/m², 15 kJ/m²·K:*

| Solar time | N | NE | E | SE | S | SW | W | NW |
|---|---|---|---|---|---|---|---|---|
| 7 | 4 | 15 | 17 | 10 | 1 | 1 | 1 | 1 |
| 8 | 5 | 20 | 26 | 18 | 3 | 3 | 3 | 3 |
| 9 | 5 | 22 | 30 | 24 | 7 | 4 | 5 | 4 |
| 10 | 7 | 20 | 31 | 27 | 12 | 6 | 6 | 6 |
| 11 | 8 | 16 | 28 | 28 | 17 | 9 | 8 | 8 |
| 12 | 10 | 15 | 22 | 27 | 22 | 14 | 10 | 10 |
| 13 | 12 | 14 | 19 | 23 | 25 | 21 | 15 | 12 |
| 14 | 13 | 15 | 17 | 18 | 24 | 33 | 31 | 20 |
| 15 | 13 | 15 | 17 | 18 | 24 | 33 | 31 | 20 |
| 16 | 14 | 14 | 16 | 16 | 21 | 35 | 37 | 26 |
| 17 | 14 | 14 | 15 | 15 | 17 | 34 | 40 | 31 |
| 18 | 15 | 12 | 13 | 13 | 14 | 29 | 37 | 31 |
| 19 | 12 | 10 | 11 | 11 | 11 | 20 | 27 | 23 |
| 20 | 8 | 8 | 8 | 8 | 8 | 13 | 16 | 14 |
| CLTD max | 15 | 22 | 31 | 28 | 26 | 35 | 40 | 31 |

*Wall type F (100-mm concrete block with 25–50 mm insulation; or 100 mm face brick with insulation), 200 kg/m², 130 kJ/m²·K:*

| Solar time | N | NE | E | SE | S | SW | W | NW |
|---|---|---|---|---|---|---|---|---|
| 7 | 1 | 3 | 4 | 2 | 1 | 1 | 2 | 1 |
| 8 | 2 | 8 | 9 | 6 | 1 | 1 | 2 | 1 |
| 9 | 3 | 13 | 16 | 10 | 2 | 2 | 2 | 2 |
| 10 | 4 | 16 | 21 | 15 | 4 | 3 | 3 | 3 |
| 11 | 5 | 17 | 24 | 20 | 7 | 4 | 4 | 4 |
| 12 | 6 | 16 | 25 | 23 | 11 | 6 | 6 | 6 |
| 13 | 8 | 16 | 24 | 24 | 15 | 10 | 8 | 7 |
| 14 | 9 | 15 | 22 | 23 | 19 | 14 | 11 | 9 |
| 15 | 11 | 15 | 20 | 22 | 21 | 20 | 16 | 12 |
| 16 | 12 | 15 | 19 | 20 | 22 | 24 | 22 | 15 |
| 17 | 12 | 15 | 18 | 19 | 21 | 28 | 27 | 19 |
| 18 | 13 | 14 | 17 | 17 | 19 | 30 | 32 | 24 |
| 19 | 13 | 13 | 15 | 16 | 17 | 29 | 33 | 26 |
| 20 | 13 | 12 | 13 | 14 | 15 | 25 | 30 | 24 |
| CLTD max | 13 | 17 | 25 | 24 | 22 | 30 | 33 | 26 |

*Wall type E (200-mm concrete block with interior and exterior finish; or 100 mm face brick with 100-mm concrete block), 300 kg/m², 230 kJ/m²·K:*

| Solar time | N | NE | E | SE | S | SW | W | NW |
|---|---|---|---|---|---|---|---|---|
| 7 | 2 | 3 | 3 | 3 | 2 | 4 | 4 | 3 |
| 8 | 2 | 5 | 6 | 4 | 2 | 3 | 3 | 3 |
| 9 | 3 | 8 | 10 | 7 | 2 | 3 | 3 | 3 |
| 10 | 3 | 11 | 15 | 10 | 3 | 3 | 4 | 3 |
| 11 | 4 | 13 | 18 | 14 | 5 | 4 | 4 | 4 |
| 12 | 5 | 14 | 20 | 17 | 7 | 5 | 5 | 5 |
| 13 | 6 | 14 | 21 | 19 | 10 | 7 | 6 | 6 |
| 14 | 7 | 14 | 21 | 20 | 14 | 10 | 8 | 7 |
| 15 | 8 | 14 | 20 | 20 | 16 | 14 | 11 | 9 |
| 16 | 10 | 15 | 19 | 20 | 18 | 18 | 15 | 11 |
| 17 | 10 | 14 | 18 | 19 | 19 | 21 | 20 | 14 |
| 18 | 11 | 14 | 18 | 18 | 18 | 24 | 24 | 18 |
| 19 | 12 | 14 | 17 | 17 | 17 | 25 | 27 | 21 |
| 20 | 12 | 13 | 15 | 16 | 16 | 24 | 27 | 21 |
| CLTD max | 12 | 15 | 21 | 20 | 19 | 25 | 27 | 21 |

*Wall type D (100 mm face brick with 200-mm concrete block; or 100 mm face brick and 100-mm common brick), 390 kg/m², 350 kJ/m²·K:*

| Solar time | N | NE | E | SE | S | SW | W | NW |
|---|---|---|---|---|---|---|---|---|
| 7 | 3 | 4 | 5 | 5 | 4 | 6 | 7 | 6 |
| 8 | 3 | 4 | 5 | 5 | 4 | 5 | 6 | 5 |
| 9 | 3 | 6 | 7 | 5 | 3 | 5 | 5 | 4 |
| 10 | 3 | 8 | 10 | 7 | 3 | 4 | 5 | 4 |
| 11 | 4 | 10 | 13 | 10 | 4 | 4 | 5 | 4 |
| 12 | 4 | 11 | 15 | 12 | 5 | 5 | 5 | 4 |
| 13 | 5 | 12 | 17 | 14 | 7 | 6 | 6 | 5 |
| 14 | 6 | 13 | 18 | 16 | 9 | 7 | 6 | 6 |
| 15 | 6 | 13 | 18 | 17 | 11 | 9 | 8 | 7 |
| 16 | 7 | 13 | 18 | 18 | 13 | 12 | 10 | 8 |
| 17 | 8 | 14 | 18 | 18 | 15 | 15 | 13 | 10 |
| 18 | 9 | 14 | 18 | 18 | 16 | 18 | 17 | 12 |
| 19 | 10 | 14 | 17 | 17 | 16 | 20 | 20 | 15 |
| 20 | 11 | 13 | 17 | 17 | 16 | 21 | 22 | 17 |
| CLTD max | 11 | 14 | 18 | 18 | 16 | 21 | 23 | 18 |

*Wall type C (200-mm concrete wall with interior and exterior finish), 530 kg/m², 450 kJ/m²·K:*

| Solar time | N | NE | E | SE | S | SW | W | NW |
|---|---|---|---|---|---|---|---|---|
| 7 | 5 | 6 | 7 | 7 | 6 | 9 | 10 | 8 |
| 8 | 4 | 6 | 7 | 6 | 6 | 8 | 9 | 7 |
| 9 | 4 | 6 | 8 | 7 | 5 | 7 | 8 | 6 |
| 10 | 4 | 7 | 9 | 7 | 5 | 7 | 7 | 6 |
| 11 | 4 | 8 | 11 | 9 | 5 | 6 | 7 | 5 |
| 12 | 4 | 10 | 13 | 10 | 5 | 6 | 7 | 5 |
| 13 | 5 | 10 | 14 | 12 | 6 | 6 | 7 | 6 |
| 14 | 5 | 11 | 15 | 13 | 8 | 7 | 7 | 6 |
| 15 | 6 | 12 | 16 | 14 | 9 | 8 | 8 | 6 |
| 16 | 6 | 12 | 16 | 15 | 11 | 10 | 9 | 7 |
| 17 | 7 | 12 | 17 | 16 | 12 | 12 | 11 | 9 |
| 18 | 8 | 13 | 17 | 16 | 13 | 14 | 13 | 10 |
| 19 | 9 | 13 | 16 | 16 | 14 | 16 | 16 | 12 |
| 20 | 9 | 13 | 16 | 16 | 14 | 18 | 18 | 14 |
| CLTD max | 9 | 13 | 17 | 16 | 14 | 18 | 20 | 15 |

> *Notes:*
> 1. Reference 4 also shows CLTD values for heavier walls.
> 2. Directly applicable for conditions stated in Table 4-14 Note 1.
> 3. Correction for differing indoor/outdoor temperatures: see Table 4-14 Note 2.
> 4. Wall constructions not listed can be approximated by using the wall with the nearest values of density and heat capacity.
> 5. For walls with additional insulation, shift to the wall with next higher mass (preceding letter) for each additional $R$ of 1.2 m²·K/W.

**Example 4-5** Determine the peak heat gain through a west-facing brick veneer wall (similar in cross section to that shown in Example 4-3), July 21 at 40° north latitude. The inside temperature is 25°C, and the average daily temperature is 30°C.

*Solution* The wall most nearly matches type F in Table 4-15. The maximum CLTD occurs at 1900 h (7 P.M.) with a value of 33°C. The average outdoor temperature is 30°C rather than 29°C, on which the table is based, so the adjusted CLTD is:

$$CLTD = 33 + (30 - 29) = 34 \text{ K}$$

From Example 4-3, $R = 2.812$ m²·K/W, so $U = 0.356$ W/m²·K.

$$\frac{q_{max}}{A} = U \times CLTD = 0.356 \times 34 = 12.1 \text{ W/m}^2$$

---

## 4-14 Summary of Procedures for Estimating Cooling Loads

The process of estimating cooling loads is similar to that used in determining heating loads:

1. Select design values for outdoor summer dry-bulb temperature (2.5 percent value), mean coincident wet-bulb temperature, and the daily average temperature from Table 4-3.
2. Select an indoor design temperature which is appropriate for the activities to be carried out in the space.
3. Determine whether any special conditions exist, such as adjacent unconditioned spaces. Estimate temperatures in the adjacent spaces.
4. On the basis of building plans and specifications, compute heat-transfer coefficients for the building components in each enclosing surface. Note that the only differences between the U values calculated here and those for the heating-load estimate are the values used for the surface convection coefficients, which differ in summer and winter.
5. From the building plans and specifications, system operating schedule, and design values of wind velocity and temperature difference, estimate the rate of infiltration and/or ventilation of outside air. For the cooling load the latent load is also included.
6. Determine the additional building characteristics, e.g., location, orientation, external shading, and mass, that will influence solar-heat gain.
7. On the basis of building components and design conditions determine the appropriate cooling-load temperature differences, solar-heat gain factors, and cooling-load factors.
8. On the basis of the heat-transfer coefficients, areas, and temperature differences determined above calculate the rate of heat gain to the space.
9. For spaces with heat gain from internal sources (lights, equipment, or people), apply the cooling-load factor when appropriate.
10. Sum all the pertinent load components to determine the maximum capacity required for heating and cooling. If the building is to be operated intermittently, additional capacity may be required.

---

## Problems

**4-1** The exterior wall of a single-story office building near Chicago is 3 m high and 15 m long. The wall consists of 100-mm face brick, 40-mm polystyrene insulating board, 150-mm lightweight concrete block, and an interior 16-mm gypsum board. The wall contains three single-glass windows 1.5 m high by 2 m long. Calculate the heat loss through the wall at design conditions if the inside temperature is 20°C. *Ans.* 2.91 kW.

**4-2** For the wall and conditions stated in Prob. 4-1 determine the percent reduction in heat loss through the wall if (a) the 40 mm of polystyrene insulation is replaced with 55 mm of cellular polyurethane, (b) the single-glazed windows are replaced with double-glazed windows with a 6-mm air space. (c) If you were to choose between modification (a) or (b) to upgrade the thermal resistance of the wall, which would you choose and why? *Ans.* (a) 12.4%

**4-3** An office in Houston, Texas, is maintained at 25°C and 55 percent relative humidity. The average occupancy is five people, and there will be some smoking. Calculate the cooling load imposed by ventilation requirements at summer design conditions with supply air conditions set at 15°C and 95 percent relative humidity if (a) the recommended rate of outside ventilation air is used and (b) if a filtration device of $E$ = 70 percent is used. *Ans.* (a) 2.1 kW, (b) 1.31 kW.

**4-4** A computer room located on the second floor of a five-story office building is 10 by 7 m. The exterior wall is 3.5 m high and 10 m long; it is a metal curtain wall (steel backed with 10 mm of insulating board), 75 mm of glass-fiber insulation, and 16 mm of gypsum board. Single-glazed windows make up 30 percent of the exterior wall. The computer and lights in the room operate 24 h/d and have a combined heat release to the space of 2 kW. The indoor temperature is 20°C. (a) If the building is located in Columbus, Ohio, determine the heating load at winter design conditions. *Ans.* 602 W. (b) What would be the load if the windows were double-glazed?

**4-5** Compute the heat gain for a window facing southeast at 32° north latitude at 10 A.M. central daylight time on August 21. The window is regular double glass with a 13-mm air space. The glass and inside draperies have a combined shading coefficient of 0.45. The indoor design temperature is 25°C, and the outdoor temperature is 37°C. Window dimensions are 2 m wide and 1.5 m high. *Ans.* 150 W

**4-6** The window in Prob. 4-5 has an 0.5-m overhang at the top of the window. How far will the shadow extend downward? *Ans.* 0.55 m.

**4-7** Compute the instantaneous heat gain for the window in Prob. 4-5 with the external shade in Prob. 4-6. *Ans.* 558 W.

**4-8** Compute the total heat gain for the south windows of an office building that has no external shading. The windows are double-glazed with a 6-mm air space and with regular plate glass inside and out. Draperies with a shading coefficient of 0.7 are fully closed. Make the calculation for 12 noon in (a) August and (b) December at 32° north latitude. The total window area is 40 m². Assume that the indoor temperatures are 25 and 20°C and that the outdoor temperatures are 37 and 4°C. *Ans.* (a) 9930 W.

**4-9** Compute the instantaneous heat gain for the south wall of a building at 32° north latitude on July 21. The time is 4 P.M. sun time. The wall is brick veneer and frame with an overall heat-transfer coefficient of 0.35 W/m²·K. The dimensions of the wall are 2.5 by 5 m. *Ans.* 87.5 W.

**4-10** Compute the peak instantaneous heat gain per square meter of area for a brick west wall similar to that in Example 4-3. Assume that the wall is located at 40° north latitude. The date is July. What time of the day does the peak occur? The outdoor daily average temperature of 30°C and indoor design temperature is 25°C.

---

## References

1. *Thermal Environmental Conditions for Human Occupancy*, Standard 55-81, American Society of Heating, Refrigerating, and Air-Conditioning Engineers, Atlanta, Ga., 1981.
2. *Standard for Ventilation Required for Minimum Acceptable Indoor Air Quality*, ASHRAE Standard 62-81, American Society of Heating, Refrigerating, and Air-Conditioning Engineers, Atlanta, Ga., 1981.
3. "Handbook and Product Directory, Equipment Volume," American Society of Heating, Refrigerating, and Air-Conditioning Engineers, Atlanta, Ga., 1979.
4. "ASHRAE Handbook, Fundamentals Volume," American Society of Heating, Refrigerating, and Air-Conditioning Engineers, Atlanta, Ga., 1981.
5. C. W. Coblentz and P. R. Achenbach: Field Measurements of Air Infiltration in Ten Electrically-Heated Houses, *ASHRAE Trans.*, vol. 69, pp. 358-365, 1963.
6. W. Rudoy: "Cooling and Heating Load Calculation Manual," American Society of Heating, Refrigerating, and Air-Conditioning Engineers, Atlanta, Ga., 1979.
