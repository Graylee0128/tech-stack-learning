# Chapter 3: Psychrometry and Wetted-Surface Heat Transfer

---

## 3-1 Importance

Psychrometry is the study of the properties of mixtures of air and water vapor. The subject is important in air-conditioning practice because atmospheric air is not completely dry but a mixture of air and water vapor. In some air-conditioning processes water is removed from the air-water-vapor mixture, and in others water is added. Psychrometric principles are applied in later chapters in this book, e.g., to load calculations, air-conditioning systems, cooling and dehumidifying coils, cooling towers, and evaporative condensers.

In some equipment there is a heat-and mass-transfer process between air and a wetted surface. Examples include some types of humidifiers, dehumidifying and cooling coils, and water-spray equipment such as cooling towers and evaporative condensers. Some convenient relations can be developed to express the rates of heat and mass transfer using enthalpy potential, discussed later in this chapter. But first the psychrometric chart is explored, property by property, followed by a discussion of the most common air-conditioning processes.

---

## 3-2 Psychrometric Chart

Since charts showing psychrometric properties are readily available (*Figure 3-1*), why should we concern ourselves with the development of a chart? Two reasons are to become aware of the bases of the chart and to be able to calculate properties at new sets of conditions, e.g., nonstandard barometric pressure.

> *[Figure 3-1] Psychrometric chart at barometric pressure = 101.325 kPa.*

The step-by-step development of the psychrometric chart that follows will make use of a few simplifying assumptions. The chart that can be developed using simple equations is reasonably accurate and can be used in most engineering calculations, but of course the most accurate chart or data available should be used.

---

## 3-3 Saturation Line

The coordinates chosen for the psychrometric chart presented in this chapter are the temperature $t$ for the abscissa and temporarily the water-vapor pressure $p_s$ for the ordinate. First consider the chart to represent water alone. The saturation line can now be drawn on the chart (*Figure 3-2*). Data for the saturation line can be obtained directly from tables of saturated water (Table A-1). The region to the right of the saturation line represents superheated water vapor. If superheated vapor is cooled at constant pressure, it will eventually reach the saturation line, where it begins to condense.

> *[Figure 3-2] Saturation line.*

Thus far, no air has been present with the water vapor. What is the effect on Figure 3-2 if air is present? Ideally, none. The water vapor continues to behave as though no air were present. At a given water-vapor pressure, which is now a partial pressure, condensation occurs at the same temperature as it would if no air were present. There actually is a slight interaction between the molecules of air and water vapor, which changes the steam-table data slightly. Table A-2 presents the properties of air saturated with water vapor. A comparison of vapor pressures of the water in the air mixture of Table A-2 with that of pure water shown in Table A-1 reveals practically no difference in pressure at a given temperature.

Figure 3-2 can now be considered applicable to an air-water-vapor mixture. If the condition of the mixture lies on the saturation line, the air is said to be **saturated**, meaning that any decrease in temperature will result in condensation of the water vapor into liquid. To the right of the saturation line the air is **unsaturated**. If point A represents the condition of the air, the temperature of that mixture will have to be reduced to temperature B in order for condensation to begin. Air at A is said to have a **dew-point temperature** of B.

---

## 3-4 Relative Humidity

The relative humidity $\phi$ is defined as the ratio of the mole fraction of water vapor in moist air to mole fraction of water vapor in saturated air at the same temperature and pressure. From perfect-gas relationships another expression for $\phi$ is:

$$\phi = \frac{\text{existing partial pressure of water vapor}}{\text{saturation pressure of pure water at same temperature}}$$

Lines of constant relative humidity can be added to the chart, as in *Figure 3-3*, by marking off vertical distances between the saturation line and the base of the chart. The relative humidity of 0.50, for example, has an ordinate equal to one-half that of the saturation line at that temperature.

> *[Figure 3-3] Relative-humidity line.*

---

## 3-5 Humidity Ratio

The humidity ratio $W$ is the mass of water interspersed in each kilogram of dry air. The humidity ratio, like the next several properties to be studied — enthalpy and specific volume — is based on 1 kg of dry air. The perfect-gas equation can be summoned to solve for the humidity ratio. Both water vapor and air may be assumed to be perfect gases in the usual air-conditioning applications.

$$W = \frac{\text{kg of water vapor}}{\text{kg of dry air}} = \frac{p_s V / R_s T}{p_a V / R_a T} = \frac{p_s / R_s}{(p_t - p_s) / R_a} \tag{3-1}$$

where:
- $W$ = humidity ratio, (kg of water vapor)/(kg of dry air)
- $V$ = arbitrary volume of air-vapor mixture, m³
- $p_t$ = atmospheric pressure = $p_a + p_s$, Pa
- $p_a$ = partial pressure of dry air, Pa
- $R_a$ = gas constant of dry air = 287 J/kg·K
- $R_s$ = gas constant of water vapor = 461.5 J/kg·K
- $T$ = absolute temperature of air-vapor mixture, K

Substituting the numerical values of $R_a$ and $R_s$ into Eq. (3-1) gives:

$$W = \frac{287}{461.5} \cdot \frac{p_s}{p_t - p_s} = 0.622 \frac{p_s}{p_t - p_s} \tag{3-2}$$

The atmospheric pressure $p_t$ has now appeared on the scene, and from this point on in the development of the psychrometric chart the chart will be unique to a given barometric pressure.

> *[Figure 3-4] Humidity ratio W as another ordinate.*

**Example 3-1** Compute the humidity ratio of air at 60 percent relative humidity when the temperature is 30°C. The barometric pressure is the standard value of 101.3 kPa.

**Solution** The water-vapor pressure of saturated air at 30°C is 4.241 kPa from Table A-1. Since the relative humidity is 60 percent, the water-vapor pressure of the air is $0.60(4.241\;\text{kPa}) = 2.545\;\text{kPa}$. From Eq. (3-2):

$$W = 0.622 \frac{2.545}{101.3 - 2.545} = 0.0160\;\text{kg/kg}$$

This result checks the value read from Figure 3-1.

---

## 3-6 Enthalpy

The enthalpy of the mixture of dry air and water vapor is the sum of the enthalpy of the dry air and the enthalpy of the water vapor. Enthalpy values are always based on some datum plane, and the zero value of the dry air is chosen as air at 0°C. The zero value of the water vapor is saturated liquid water at 0°C, the same datum plane that is used for tables of steam. An equation for the enthalpy is:

$$h = c_p t + W h_g \quad \text{kJ/kg dry air} \tag{3-3}$$

where:
- $c_p$ = specific heat of dry air at constant pressure = 1.0 kJ/kg·K
- $t$ = temperature of air-vapor mixture, °C
- $h_g$ = enthalpy of saturated steam at temperature of air-vapor mixture, kJ/kg

Equation (3-3) gives quite accurate results, although several refinements can be made. The specific heat $c_p$ actually varies from 1.006 at 0°C to 1.009 at 50°C. The enthalpy of water vapor $h_g$ is for saturated steam, but the water vapor in the air-vapor mixture is likely to be superheated. No appreciable error results, however, because of the fortunate relationship of enthalpy and temperature shown on the Mollier diagram of *Figure 3-5*.

> *[Figure 3-5] Line of constant temperature shows that the enthalpy of superheated water vapor is approximately equal to the enthalpy of saturated vapor at the same temperature.*

> *[Figure 3-6] Line of constant enthalpy.*

**Example 3-2** Locate the point on the 95 kJ/kg enthalpy line where the temperature is 50°C.

**Solution** At $t = 50°C$, $h_g = 2592$ kJ/kg from Table A-1. Solving for $W$ from Eq. (3-3) for $h = 95$ kJ/kg gives:

$$W = \frac{95 - 1.0(50)}{2592} = 0.0174\;\text{kg/kg}$$

The lines within the confines of the saturation line and the axes on Figure 3-1 are not the lines of constant enthalpy but lines of constant wet-bulb temperature (Sec. 3-9), which deviate slightly from lines of constant enthalpy. Lines of constant enthalpy are shown to the left of the saturation line in Figure 3-1, and their continuations are shown at the right and bottom borders of the chart.

---

## 3-7 Specific Volume

The perfect-gas equation is used to calculate the specific volume of the air-vapor mixture. The specific volume is the number of cubic meters of mixture per kilogram of dry air.

From the perfect-gas equation, the specific volume $v$ is:

$$v = \frac{R_a T}{p_a} = \frac{R_a T}{p_t - p_s} \quad \text{m}^3\text{/kg dry air} \tag{3-4}$$

> *[Figure 3-7] Line of constant specific volume.*

**Example 3-3** What is the specific volume of an air-water-vapor mixture having a temperature of 24°C and a relative humidity of 20 percent at standard barometric pressure?

**Solution** The water-vapor pressure of saturated air at 24°C is, from Table A-1, 2.982 kPa; so the vapor pressure with a relative humidity of 20 percent is $0.2(2.982) = 0.5964\;\text{kPa} = 596.4\;\text{Pa}$. Applying Eq. (3-4):

$$v = \frac{287(24 + 273.15)}{101{,}300 - 596} = 0.85\;\text{m}^3\text{/kg dry air}$$

This result checks the value from Figure 3-1.

---

## 3-8 Combined Heat and Mass Transfer; the Straight-Line Law

The final psychrometric property to be considered is the wet-bulb temperature, but in order to improve our understanding of this property a short detour will be made. It leads into the combined process of heat and mass transfer and proposes the **straight-line law**. This law states that when air is transferring heat and mass (water) to or from a wetted surface, the condition of the air shown on a psychrometric chart drives toward the saturation line at the temperature of the wetted surface.

> *[Figure 3-8] Heat and mass transfer between air and a wetted surface.*

> *[Figure 3-9] Condition of air drives toward saturation line at temperature of wetted surface.*

If air flows over a wetted surface, the condition of air passing over differential area $dA$ changes from condition 1 to condition 2 on the psychrometric chart. The straight-line law asserts that point 2 lies on a straight line drawn between point 1 and the saturation curve at the wetted-surface temperature.

It is no surprise that the warm air at 1 drops in temperature when in contact with water at temperature $t_w$. It is also to be expected that the air at 1, having a higher vapor pressure than the liquid at temperature $t_w$, will transfer mass by condensing some water vapor and dropping the humidity ratio of the air. What is unique is that the rates of heat and mass transfer are so related that the path is a straight line driving toward the saturation line at the wetted-surface temperature. This special property is due to the value of unity of the Lewis relation, a dimensionless group that will be explained in Sec. 3-14.

---

## 3-9 Adiabatic Saturation and Thermodynamic Wet-Bulb Temperature

An **adiabatic saturator** (*Figure 3-10*) is a device in which air flows through a spray of water. The water circulates continuously, and the spray provides so much surface area that the air leaves the spray chamber in equilibrium with the water, with respect to both temperature and vapor pressure. The device is adiabatic in that the walls of the saturator are insulated, and no heat is added to, or extracted from, the water line that circulates the water from the sump back to the sprays. In order to perpetuate the process it is necessary to provide makeup water to compensate for the amount of water evaporated into the air.

> *[Figure 3-10] Adiabatic saturation.*

After the adiabatic saturator has achieved a steady-state condition, the temperature indicated by an accurate thermometer immersed in the sump is the **thermodynamic wet-bulb temperature**. Certain combinations of air conditions will result in a given sump temperature and can be defined by writing an energy balance about the saturator:

$$h_1 + (W_2 - W_1) h_f = h_2 \tag{3-5}$$

where $h_f$ is the enthalpy of saturated liquid at the sump or thermodynamic wet-bulb temperature.

> *[Figure 3-11] Line of constant thermodynamic wet-bulb temperature.*

On the psychrometric chart in Figure 3-11, point 1 lies below the line of constant enthalpy that passes through point 2. Any other condition of air that results in the same sump temperature, such as point 1', has the same wet-bulb temperature. This line is straight because of the straight-line law.

Lines of constant wet-bulb temperature are shown on psychrometric charts, as in Figure 3-1, but lines of constant enthalpy are rarely shown. The enthalpy scale to the left of the saturation line applies to air that is saturated. For unsaturated air the enthalpy scale on the left must be combined with the enthalpy scale shown at the right and bottom borders of the chart.

---

## 3-10 Deviation between Enthalpy and Wet-Bulb Lines

As Figure 3-11 indicates, readings of enthalpy obtained by following the wet-bulb line to the saturation curve specify values of enthalpy that are too high. The psychrometric chart, Figure 3-1, shows lines of constant thermodynamic wet-bulb temperature and not lines of constant enthalpy. The enthalpy scale shown at the left applies only to the conditions on the saturation line, and both the scale at the left and the scales at the right and bottom borders should be used for more precise determinations of enthalpy.

To check an enthalpy deviation, compare the chart reading with a calculation for air having a dry-bulb temperature of 40°C and a relative humidity of 41 percent. The wet-bulb temperature of air at this condition is 28°C.

In Figure 3-1 a straightedge can be set at 40°C dry-bulb temperature and 41 percent relative humidity and pivoted about that point until the enthalpy values on the left and right enthalpy scales match. That value is 89 kJ/kg.

Equation (3-5) permits calculation of the enthalpy of the point in question, $h_1$, by correcting the value of $h_2$ (the enthalpy of saturated air at the same wet-bulb temperature):

$$h_1 = 89.7 - 117.3(0.0241 - 0.019) = 89.1\;\text{kJ/kg}$$

where $W_1 = 0.019$ kg/kg, $W_2 = 0.0241$ kg/kg, and $h_f = h_f$ at 28°C = 117.3 kJ/kg.

---

## 3-11 Wet-Bulb Thermometer

Although the adiabatic saturator of Figure 3-10 is not a convenient device for routine measurements, a thermometer having a wetted wick, as in *Figure 3-12*, would be convenient. We must therefore determine whether the wet-bulb thermometer truly indicates the thermodynamic wet-bulb temperature.

> *[Figure 3-12] (a) The wet-bulb temperature, and (b) the process on a psychrometric chart.*

The wetted area of the wick is finite, rather than infinite like the saturator in Figure 3-10, so the change in state of air passing over the wetted bulb can be represented by process 1-2 in Figure 3-12b. Since the energy balance about the bulb is:

$$h_1 + W_1 h_f = h_2 + W_2 h_f$$

points 1 and 2 lie on the same thermodynamic wet-bulb line. The important question, however, is: What is the temperature of the water on the wick? The answer, which comes from the application of the straight-line law, is that the condition of the air starting at point 1 has been driving toward the saturation line at the temperature of the wetted surface in order to reach point 2.

Carrier, in his pioneer paper on psychrometry, assumed that the temperature of water on a wet-bulb thermometer was the same as that in an adiabatic saturator. Lewis in 1922 grouped the terms that bear his name and concluded that a value of unity of this dimensionless group results in identical temperatures of a wetted wick and adiabatic spray. In 1933 Lewis demonstrated that in atmospheres other than air and water vapor the reading of a wet-bulb thermometer and the saturated spray are different. We shall hereafter consider the temperature of the wet-bulb thermometer and the adiabatic spray to be the same and drop the qualification "thermodynamic" on the wet-bulb temperature, simply calling it the **wet-bulb temperature**.

---

## 3-12 Processes

Processes performed on air can be plotted on the psychrometric chart for quick visualization. Of even more importance is the fact that the chart can be used to determine changes in such significant properties as temperature, humidity ratio, and enthalpy for the processes. Some of the basic processes will now be shown:

### 1. Sensible Heating or Cooling

Sensible heating or cooling refers to a rate of heat transfer attributable only to a change in dry-bulb temperature of the air. *Figure 3-13* shows a change in dry-bulb temperature with no change in humidity ratio.

> *[Figure 3-13] Sensible heating or cooling.*

### 2. Humidification

Humidification, as shown in *Figure 3-14*, may be adiabatic (process 1-2), or with addition of heat (process 1-3).

> *[Figure 3-14] Humidification.*

### 3. Cooling and Dehumidification

Cooling and dehumidification results in a reduction of both the dry-bulb temperature and the humidity ratio (*Figure 3-15*). A cooling and dehumidifying coil performs such a process. The refrigeration capacity in kilowatts during a cooling and dehumidifying process is given by:

$$\text{Refrigeration capacity} = w(h_1 - h_2)$$

where $w$ is in kilograms per second and $h_1$ and $h_2$ in kilojoules per kilogram.

> *[Figure 3-15] Cooling and dehumidification.*

### 4. Chemical Dehumidification

In the process of chemical dehumidification (*Figure 3-16*) the water vapor from the air is absorbed or adsorbed by a hygroscopic material. Since the process, if thermally isolated, is essentially one of constant enthalpy, and since the humidity ratio decreases, the temperature of the air must increase.

> *[Figure 3-16] Chemical dehumidification.*

### 5. Mixing

Mixing of two streams of air is a common process in air conditioning. *Figure 3-17a* shows the mixing of $w_1$ kg/s of air at condition 1 with $w_2$ kg/s of air at condition 2. The result is condition 3, shown on the psychrometric chart in *Figure 3-17b*.

> *[Figure 3-17] (a) Schematic arrangement of mixing process. (b) Mixing process on psychrometric chart.*

The fundamental equations applicable to the mixing process are an energy balance and a mass balance:

**Energy balance:**

$$w_1 h_1 + w_2 h_2 = (w_1 + w_2) h_3 \tag{3-6}$$

**Mass balance of water:**

$$w_1 W_1 + w_2 W_2 = (w_1 + w_2) W_3 \tag{3-7}$$

Equations (3-6) and (3-7) show that the final enthalpy and humidity ratio are weighted averages of the entering enthalpies and humidity ratios. An approximation used by many engineers is that the final temperature and humidity ratio are weighted averages of the entering values. With that approximation, the point on the psychrometric chart representing the result of a mixing process lies on a straight line connecting the points representing the entering conditions. Furthermore, the ratio of distances on the line, (1-3)/(2-3), equals the ratio of the flow rates, $w_2/w_1$. The error of this approximation is usually less than 1 percent.

---

## 3-13 Comment on the Basis of 1 kg of Dry Air

The enthalpy, humidity ratio, and specific volume are all based on 1 kg of dry air. A review of some of the processes presented in Sec. 3-12 shows the usefulness of the basis of dry air. In the processes shown in Figures 3-14 to 3-16 the total mass changes throughout the process because of the addition or extraction of water. If total mass of mixture were used as the basis, it would be necessary to recalculate the mass flow rate after each of these processes. The flow rate of dry air, however, remains constant through the processes.

---

## 3-14 Transfer of Sensible and Latent Heat with a Wetted Surface

When air flows past a wetted surface, as shown in *Figure 3-18*, there is a likelihood of transfer of both sensible and latent heat.

> *[Figure 3-18] Heat and mass transfer between air and a wetted surface.*

The rate of sensible-heat transfer from the water surface to the air $q_s$ can be calculated by the convection equation:

$$dq_s = h_c \, dA \, (t_i - t_a) \tag{3-8}$$

where:
- $q_s$ = rate of sensible-heat transfer, W
- $h_c$ = convection coefficient, W/m²·K
- $A$ = area, m²

The rate of mass transfer from the water surface to the air is proportional to the pressure difference. Since the humidity ratio is approximately proportional to the vapor pressure:

$$\text{rate of mass transfer} = h_D \, dA \, (W_i - W_a) \quad \text{kg/s}$$

where:
- $h_D$ = proportionality constant, kg/m²
- $W_i$ = humidity ratio of saturated air at wetted-surface temperature

Since the mass transferred causes a transfer of heat due to the condensation or evaporation:

$$dq_L = h_D \, dA \, (W_i - W_a) h_{fg} \tag{3-9}$$

where:
- $q_L$ = rate of latent-heat transfer, W
- $h_{fg}$ = latent heat of water at $t_i$, J/kg

The proportionality between $h_D$ and $h_c$ is expressed by:

$$h_D = \frac{h_c}{c_{pm}} \tag{3-10}$$

where $c_{pm}$ is the specific heat of moist air, J/kg·K:

$$c_{pm} = c_p + W c_{ps} \tag{3-11}$$

---

## 3-15 Enthalpy Potential

The concept of **enthalpy potential** is a useful one in quantifying the transfer of total heat (sensible plus latent) in those processes and components where there is direct contact between air and water.

The expression for transfer of total heat $dq_t$ through a differential area $dA$ is available from a combination of Eqs. (3-8) and (3-9):

$$dq_t = dq_s + dq_L = h_c \, dA \, (t_i - t_a) + h_D \, dA \, (W_i - W_a) h_{fg}$$

Applying the expression for $h_D$ from Eq. (3-10) and substituting Eq. (3-11):

$$dq_t = \frac{h_c \, dA}{c_{pm}} [(c_p t_i + W_i h_{fg}) - (c_p t_a + W_a c_{ps} t_a - W_a c_{ps} t_i + W_a h_{fg})] \tag{3-12}$$

Adding the nearly negligible expression $W_i h_f - W_a h_f$ (where $h_f$ is the enthalpy of saturated liquid water at temperature $t_i$), the equation becomes:

$$dq_t = \frac{h_c \, dA}{c_{pm}} [(c_p t_i + W_i h_{fg} + W_i h_f) - (c_p t_a + W_a h_g)] \tag{3-13}$$

The expression in the first set of brackets is precisely the enthalpy of saturated air at the wetted-surface temperature, and the expression in the second set is precisely the enthalpy of the air in the free stream. Thus:

$$dq_t = \frac{h_c \, dA}{c_{pm}} (h_i - h_a) \tag{3-14}$$

The name **enthalpy potential** originates from Eq. (3-14) because the potential for the transfer of the sum of sensible and latent heats is the difference between the enthalpy of saturated air at the wetted-surface temperature $h_i$ and the enthalpy of air in the free stream $h_a$.

The specific heat of moist air $c_{pm}$ is expressed by Eq. (3-11), but for states of air near those of normal room conditions a value of **1.02 kJ/kg·K** may be used.

---

## 3-16 Insights Provided by Enthalpy Potential

In addition to helping quantify the calculations of heat and mass transfer in cooling and dehumidifying coils, sprayed coils, evaporative condensers, and cooling towers, the enthalpy potential provides a qualitative indication of the direction of total heat flow. Three different cases are illustrated:

> *[Figure 3-19] Case 1, $q_t$ from air to water.*

> *[Figure 3-20] Case 2, $q_t$ from air to water.*

> *[Figure 3-21] Case 3, $q_t$ from the water to air.*

**Case 1:**
- $dq_s$ is from the air to the water since $t_a > t_i$
- $dq_L$ is from the air to the water since $W_a > W_i$
- $dq_t$ is from the air to the water since $h_a > h_i$

**Case 2:**
- $dq_s$ is from the air to the water since $t_a > t_i$
- $dq_L$ is from the water to the air since $W_a < W_i$
- $dq_t$ is from the air to the water since $h_a > h_i$

Before the concept of enthalpy potential was developed, we were unable to determine immediately which way $dq_t$ was flowing because we did not know the relative magnitudes of $dq_s$ and $dq_L$. Now the relative values of $h_a$ and $h_i$ provide the clue.

**Case 3:**
- $dq_s$ is from the air to the water since $t_a > t_i$
- $dq_L$ is from the water to the air since $W_a < W_i$
- $dq_t$ is from the water to the air since $h_a < h_i$

An interesting situation occurs in Case 3, where heat flows from the low-temperature water to the high-temperature air. The second law of thermodynamics is not violated, however, because the transfer due to the difference in partial pressure of the water vapor must also be considered.

---

## Problems

**3-1** Calculate the specific volume of an air-vapor mixture in cubic meters per kilogram of dry air when the following conditions prevail: $t = 30°C$, $W = 0.015$ kg/kg, and $p_t = 90$ kPa. *Ans. 0.99 m³/kg.*

**3-2** A sample of air has a dry-bulb temperature of 30°C and a wet-bulb temperature of 25°C. The barometric pressure is 101 kPa. Using steam tables and Eqs. (3-2), (3-3), and (3-5), calculate:
- (a) the humidity ratio if this air is adiabatically saturated
- (b) the enthalpy of the air if it is adiabatically saturated
- (c) the humidity ratio of the sample using Eq. (3-5)
- (d) the partial pressure of water vapor in the sample
- (e) the relative humidity

*Ans. (a) 0.0201 kg/kg, (b) 76.2 kJ/kg, (c) 0.0180 kg/kg, (d) 2840 Pa, (e) 67%.*

**3-3** Using humidity ratios from the psychrometric chart, calculate the error in considering the wet-bulb line to be the line of constant enthalpy at the point of 35°C dry-bulb temperature and 50 percent relative humidity.

**3-4** An air-vapor mixture has a dry-bulb temperature of 30°C and a humidity ratio of 0.015. Calculate at two different barometric pressures, 85 and 101 kPa:
- (a) the enthalpy
- (b) the dew-point temperature

*Ans. (a) 68.3 and 68.3 kJ/kg, (b) 17.5 and 20.3°C.*

**3-5** A cooling tower is a device that cools a spray of water by passing it through a stream of air. If 15 m³/s of air at 35°C dry-bulb and 24°C wet-bulb temperature and an atmospheric pressure of 101 kPa enters the tower and the air leaves saturated at 31°C:
- (a) to what temperature can this airstream cool a spray of water entering at 38°C with a flow rate of 20 kg/s?
- (b) how many kilograms per second of makeup water must be added to compensate for the water that is evaporated?

*Ans. (a) 31.3°C, (b) 0.245 kg/s.*

**3-6** In an air-conditioning unit 3.5 m³/s of air at 27°C dry-bulb temperature, 50 percent relative humidity, and standard atmospheric pressure enters the unit. The leaving condition of the air is 13°C dry-bulb temperature and 90 percent relative humidity. Using properties from the psychrometric chart:
- (a) calculate the refrigerating capacity in kilowatts
- (b) determine the rate of water removal from the air

*Ans. (a) 88 kW, (b) 0.0113 kg/s.*

**3-7** A stream of outdoor air is mixed with a stream of return air in an air-conditioning system that operates at 101 kPa pressure. The flow rate of outdoor air is 2 kg/s, and its condition is 35°C dry-bulb temperature and 25°C wet-bulb temperature. The flow rate of return air is 3 kg/s, and its condition is 24°C and 50 percent relative humidity. Determine:
- (a) the enthalpy of the mixture
- (b) the humidity ratio of the mixture
- (c) the dry-bulb temperature of the mixture from the properties determined in parts (a) and (b)
- (d) the dry-bulb temperature by weighted average of the dry-bulb temperatures of the entering streams

*Ans. (a) 59.1 kJ/kg, (b) 0.01198 kg/kg, (c) 28.6°C, (d) 28.4°C.*

**3-8** The air conditions at the intake of an air compressor are 28°C, 50 percent relative humidity, and 101 kPa. The air is compressed to 400 kPa, then sent to an intercooler. If condensation of water vapor from the compressed air is to be prevented, what is the minimum temperature to which the air can be cooled in the intercooler? *Ans. 40.3°C.*

**3-9** A winter air-conditioning system adds for humidification 0.0025 kg/s of saturated steam at 101 kPa pressure to an airflow of 0.36 kg/s. The air is initially at a temperature of 15°C with a relative humidity of 20 percent. What are the dry- and wet-bulb temperatures of the air leaving the humidifier? *Ans. 16.0 and 13.8°C.*

**3-10** Determine for the three cases listed below the magnitude in watts and the direction of transfer of sensible heat [using Eq. (3-8)], latent heat [using Eq. (3-9)], and total heat [using Eq. (3-14)]. The area is 0.15 m² and $h_c = 30$ W/m²·K. Air at 30°C and 50 percent relative humidity is in contact with water that is at a temperature of:
- (a) 13°C
- (b) 20°C
- (c) 28°C

*Ans. (a) −76.5, −42.3, −120.4 W; (b) −45.0, 15.1, −29.6 W; (c) −9.0, 116.5, 113.8 W.*

---

## References

1. Carrier, W. H.: Rational Psychrometric Formulae, ASME Trans., vol. 33, p. 1005, 1911.
2. Lewis, W. K.: The Evaporation of a Liquid into a Gas, Trans. ASME, vol. 44, p. 325, 1922.
3. Lewis, W. K.: The Evaporation of a Liquid into a Gas — A Correction, Mech. Eng., vol. 55, p. 1567, September 1933.
4. Stoecker, W. F.: "Principles for Air Conditioning Practice," Industrial Press, Inc., New York, 1968.
