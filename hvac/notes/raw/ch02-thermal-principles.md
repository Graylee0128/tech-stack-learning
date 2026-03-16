# Chapter 2: Thermal Principles

---

## 2-1 Roots of Refrigeration and Air Conditioning

Since a course in air conditioning and refrigeration might easily be titled *Applications of Thermodynamics and Heat Transfer*, it is desirable to begin the technical portion of this text with a brief review of the basic elements of these subjects. This chapter extracts some of the fundamental principles that are important for calculations used in the design and analysis of thermal systems for buildings and industrial processes. The presentation of these principles is intended to serve a very specific purpose and makes no attempt to cover the full range of applications of thermodynamics and heat transfer. Readers who feel the need of a more formal review are directed to basic texts in these subjects.

This chapter does, however, attempt to present the material in a manner which establishes a pattern of analysis that will be applied repeatedly throughout the remainder of the text. This process involves the identification of the essential elements of the problem or design, the use of simplifications or idealizations to model the system to be designed or analyzed, and the application of the appropriate physical laws to obtain the necessary result.

---

## 2-2 Concepts, Models, and Laws

Thermodynamics and heat transfer have developed from a general set of concepts, based on observations of the physical world, the specific models, and laws necessary to solve problems and design systems. Mass and energy are two of the basic concepts from which engineering science grows. From our own experience we all have some idea what each of these is but would probably find it difficult to provide a simple, concise, one-paragraph definition of either mass or energy. However, we are well enough acquainted with these concepts to realize that they are essential elements in our description of the physical world in which we live.

As the physical world is extremely complex, it is virtually impossible to describe it precisely. Even if it were, such detailed descriptions would be much too cumbersome for engineering purposes. One of the most significant accomplishments of engineering science has been the development of models of physical phenomena which, although they are approximations, provide both a sufficiently accurate description and a tractable means of solution. Newton's model of the relationship of force to mass and acceleration is an example. Although it cannot be applied universally, within its range of application it is accurate and extremely useful.

Models in and of themselves, however, are of little value unless they can be expressed in appropriate mathematical terms. The mathematical expressions of models provide the basic equations, or laws, which allow engineering science to explain or predict natural phenomena. The first and second laws of thermodynamics and the heat-transfer rate equations provide pertinent examples here. In this text we shall be discussing the use of these concepts, models, and laws in the description, design, and analysis of thermal systems in buildings and the process industries.

---

## 2-3 Thermodynamic Properties

Another essential element in the analysis of thermal systems is the identification of the pertinent thermodynamic properties. A property is any characteristic or attribute of matter which can be evaluated quantitatively. Temperature, pressure, and density are all properties. Work and heat transfer can be evaluated in terms of changes in properties, but they are not properties themselves. A property is something matter "has." Work and heat transfer are things that are "done" to a system to change its properties. Work and heat can be measured only at the boundary of the system, and the amount of energy transferred depends on how a given change takes place.

As thermodynamics centers on energy, all thermodynamic properties are related to energy. The thermodynamic state or condition of a system is defined by the values of its properties. In our considerations we shall examine equilibrium states and find that for a simple substance two intensive thermodynamic properties define the state. For a mixture of substances, e.g., dry air and water vapor, it is necessary to define three thermodynamic properties to specify the state. Once the state of the substance has been determined, all the other thermodynamic properties can be found since they are not all independently variable.

The thermodynamic properties of primary interest in this text are temperature, pressure, density and specific volume, specific heat, enthalpy, entropy, and the liquid-vapor property of state.

### Temperature

The temperature $t$ of a substance indicates its thermal state and its ability to exchange energy with a substance in contact with it. Thus, a substance with a higher temperature passes energy to one with a lower temperature. Reference points on the Celsius scale are the freezing point of water (0°C) and the boiling point of water (100°C).

Absolute temperature $T$ is the number of degrees above absolute zero expressed in kelvins (K); thus $T = t\,°C + 273$. Since temperature intervals on the two scales are identical, differences between Celsius temperatures are stated in kelvins.

### Pressure

Pressure $p$ is the normal (perpendicular) force exerted by a fluid per unit area against which the force is exerted. Absolute pressure is the measure of pressure above zero; gauge pressure is measured above existing atmospheric pressure.

The unit used for pressure is newtons per square meter (N/m²), also called a pascal (Pa). The newton is a unit of force.

Standard atmospheric pressure is 101,325 Pa = 101.3 kPa.

Pressures are measured by such instruments as pressure gauges or manometers, shown schematically installed in the air duct of *Figure 2-1*.

> *[Figure 2-1] Indicating the gauge pressure of air in a duct with a pressure gauge and a manometer.*

### Density and Specific Volume

The density $\rho$ of a fluid is the mass occupying a unit volume; the specific volume $v$ is the volume occupied by a unit mass. The density and specific volumes are reciprocals of each other. The density of air at standard atmospheric pressure and 25°C is approximately 1.2 kg/m³.

**Example 2-1** What is the mass of air contained in a room of dimensions 4 by 6 by 3 m if the specific volume of the air is 0.83 m³/kg?

**Solution** The volume of the room is 72 m³, and so the mass of air in the room is:

$$m = \frac{72\;\text{m}^3}{0.83\;\text{m}^3/\text{kg}} = 86.7\;\text{kg}$$

### Specific Heat

The specific heat of a substance is the quantity of energy required to raise the temperature of a unit mass by 1 K. Since the magnitude of this quantity is influenced by how the process is carried out, how the heat is added or removed must be described. The two most common descriptions are specific heat at constant volume $c_v$ and specific heat at constant pressure $c_p$. The second is the more useful to us because it applies to most of the heating and cooling processes experienced in air conditioning and refrigeration.

The approximate specific heats of several important substances are:

| Substance | $c_p$ |
|-----------|-------|
| Dry air | 1.0 kJ/kg·K |
| Liquid water | 4.19 kJ/kg·K |
| Water vapor | 1.88 kJ/kg·K |

**Example 2-2** What is the rate of heat input to a water heater if 0.4 kg/s of water enters at 82°C and leaves at 93°C?

**Solution** The pressure of water remains essentially constant as it flows through the heater, so $c_p$ is applicable. The amount of energy in the form of heat added to each kilogram is:

$$(4.19\;\text{kJ/kg·K})(93 - 82\;°\text{C}) = 46.1\;\text{kJ/kg}$$

The units on opposite sides of equations must balance, but the °C and K do cancel because the specific heat implies a change in temperature expressed in kelvins and 93 − 82 is a change in temperature of 11°C. A change of temperature in Celsius degrees of a given magnitude is the same change in kelvins. To complete Example 2-2, consider the fact that 0.4 kg/s flows through the heater. The rate of heat input then is:

$$(0.4\;\text{kg/s})(46.1\;\text{kJ/kg}) = 18.44\;\text{kJ/s} = 18.44\;\text{kW}$$

### Enthalpy

If the constant-pressure process introduced above is further restricted by permitting no work to be done on the substance, e.g., by a compressor, the amount of heat added or removed per unit mass is the change in enthalpy of the substance. Tables and charts of enthalpy $h$ are available for many substances. These enthalpy values are always based on some arbitrarily chosen datum plane. For example, the datum plane for water and steam is an enthalpy value of zero for liquid water at 0°C. Based on that datum plane, the enthalpy of liquid water at 100°C is 419.06 kJ/kg and of water vapor (steam) at 100°C is 2676 kJ/kg.

Since the change in enthalpy is that amount of heat added or removed per unit mass in a constant-pressure process, the change in enthalpy of the water in Example 2-2 is 46.1 kJ/kg. The enthalpy property can also express the rates of heat transfer for processes where there is vaporization or condensation, e.g., in a water boiler or an air-heating coil where steam condenses.

**Example 2-3** A flow rate of 0.06 kg/s of water enters a boiler at 90°C, at which temperature the enthalpy is 376.9 kJ/kg. The water leaves as steam at 100°C. What is the rate of heat added by the boiler?

**Solution** The change in enthalpy in this constant-pressure process is:

$$\Delta h = 2676 - 377\;\text{kJ/kg} = 2299\;\text{kJ/kg}$$

The rate of heat transfer to the water in converting it to steam is:

$$(0.06\;\text{kg/s})(2299\;\text{kJ/kg}) = 137.9\;\text{kW}$$

### Entropy

Although entropy $s$ has important technical and philosophical connotations, we shall use this property in a specific and limited manner. Entropy does appear in many charts and tables of properties and is mentioned here so that it will not be unfamiliar. The following are two implications of this property:

1. If a gas or vapor is compressed or expanded frictionlessly without adding or removing heat during the process, the entropy of the substance remains constant.
2. In the process described in implication 1, the change in enthalpy represents the amount of work per unit mass required by the compression or delivered by the expansion.

Possibly the greatest practical use we shall have for entropy is to read lines of constant entropy on graphs in computing the work of compression in vapor-compression refrigeration cycles.

### Liquid-Vapor Properties

Most heating and cooling systems use substances that pass between liquid and vapor states in their cycle. Steam and refrigerants are prime examples of these substances. Since the pressures, temperatures, and enthalpies are key properties during these changes, the relationships of these properties are listed in tables or displayed on charts, e.g., the pressure-enthalpy diagram for water shown in *Figure 2-2*.

The three major regions on the chart are: (1) the subcooled-liquid region to the left, (2) the liquid-vapor region in the center, and (3) the superheated-vapor region on the right. In region 1 only liquid exists, in region 3 only vapor exists, and in region 2 both liquid and vapor exist simultaneously. Separating region 2 and region 3 is the saturated-vapor line. As we move to the right along a horizontal line at constant pressure from the saturated-liquid line to the saturated-vapor line, the mixture of liquid and vapor changes from 100 percent liquid to 100 percent vapor.

Three lines of constant temperature are shown in Figure 2-2, $t = 50°C$, $t = 100°C$, and $t = 150°C$. Corresponding to our experience, water boils at a higher temperature when the pressure is higher. If the pressure is 12.3 kPa, water boils at 50°C, but at standard atmospheric pressure of 101 kPa it boils at 100°C.

Also shown in the superheated vapor region are two lines of constant entropy.

> *[Figure 2-2] Skeleton pressure-enthalpy diagram for water.*

**Example 2-4** If 9 kg/s of liquid water at 50°C flows into a boiler, is heated, boiled, and superheated to a temperature of 150°C and the entire process takes place at standard atmospheric pressure, what is the rate of heat transfer to the water?

**Solution** The process consists of three distinct parts: (1) bringing the temperature of the subcooled water up to its saturation temperature, (2) converting liquid at 100°C into vapor at 100°C, and (3) superheating the vapor from 100 to 150°C. The rate of heat transfer is the product of the mass rate of flow multiplied by the change in enthalpy. The enthalpy of entering water at 50°C and 101 kPa is 209 kJ/kg, which can be read approximately from Figure 2-2 or determined more precisely from Appendix Table A-1. The enthalpy of superheated steam at 150°C and 101 kPa is 2745 kJ/kg. The rate of heat transfer is:

$$q = (9\;\text{kg/s})(2745 - 209\;\text{kJ/kg}) = 22{,}824\;\text{kW}$$

### Perfect-Gas Law

The idealized model of gas behavior which relates the pressure, temperature, and specific volume of a perfect gas provides an example:

$$pv = RT$$

where:
- $p$ = absolute pressure, Pa
- $v$ = specific volume, m³/kg
- $R$ = gas constant = 287 J/kg·K for air and 462 J/kg·K for water
- $T$ = absolute temperature, K

For our purposes the perfect-gas equation is applicable to dry air and to highly superheated water vapor and not applicable to water and refrigerant vapors close to their saturation conditions.

**Example 2-5** What is the density of dry air at 101 kPa and 25°C?

**Solution** The density $\rho$ is the reciprocal of the specific volume $v$, and so:

$$\rho = \frac{1}{v} = \frac{p}{RT} = \frac{101{,}000\;\text{Pa}}{(287\;\text{J/kg·K})(25 + 273\;\text{K})} = 1.18\;\text{kg/m}^3$$

---

## 2-4 Thermodynamic Processes

In discussing thermodynamic properties, we have already introduced several thermodynamic processes (heating and cooling), but we must review several more definitions and the basic models and laws we shall use before expanding this discussion to a wider range of applications.

As energy is the central concept in thermodynamics, its fundamental models and laws have been developed to facilitate energy analyses, e.g., to describe energy content and energy transfer. Energy analysis is fundamentally an accounting procedure. In any accounting procedure whatever it is that is under consideration must be clearly identified. In this text we use the term **system** to designate the object or objects considered in the analysis or discussion. A system may be as simple as a specified volume of a homogeneous fluid or as complex as the entire thermal-distribution network in a large building. In most cases we shall define a system in terms of a specified region in space (sometimes referred to as a **control volume**) and entirely enclosed by a closed surface, referred to as the **system boundary** (or control surface). The size of the system and the shape of the system boundary are arbitrary and are specified for each problem so that they simplify accounting for the changes in energy storage within the system or energy transfers across a system boundary. Whatever is not included in the system is called the **environment**.

Consider the simple flow system shown in *Figure 2-3*, where mass is transferred from the environment to the system at point 1 and from the system to the environment at point 2. Such a system could be used to analyze something as simple as a pump or as complex as an entire building. The definition of the system provides the framework for the models used to describe the real objects considered in thermodynamic analysis.

> *[Figure 2-3] Conservation of mass in a simple flow system.*

---

## 2-5 Conservation of Mass

Mass is a fundamental concept and thus is not simply defined. A definition is often presented by reference to Newton's law:

$$\text{Force} = ma = m \frac{dV}{d\theta}$$

where:
- $m$ = mass, kg
- $a$ = acceleration, m/s²
- $V$ = velocity, m/s
- $\theta$ = time, s

An object subjected to an unbalanced force accelerates at a rate dependent upon the magnitude of the force. In this context the mass of an object is conceived of as being characteristic of its resistance to change in velocity.

The principle of conservation of mass states that mass is neither created nor destroyed in the processes analyzed. It may be stored within a system or transferred between a system and its environment, but it must be accounted for in any analysis procedure.

Consider Figure 2-3 again. During a time increment $d\theta$, mass $\delta m_1$ enters the system and an increment $\delta m_2$ leaves. If the mass in the system at time $\theta$ is $m_\theta$ and that at time $\theta + \delta\theta$ is $m_{\theta + \delta\theta}$, conservation of mass requires that:

$$m_{\theta + \delta\theta} - m_\theta + \delta m_2 - \delta m_1 = 0$$

If we express the mass flux as $\dot{m} = \delta m / \delta\theta$, the rate of change at any instant is:

$$\frac{dm}{d\theta} + \dot{m}_2 - \dot{m}_1 = 0$$

If the rate of change of mass within the system is zero ($dm/d\theta = 0$), then $\dot{m}_1 = \dot{m}_2$ and we have **steady flow**. Steady flow will be encountered frequently in our analysis.

---

## 2-6 Steady-Flow Energy Equation

In most air-conditioning and refrigeration systems the mass flow rates do not change from one instant to the next (or if they do, the rate of change is small); therefore the flow rate may be assumed to be steady. In the system shown symbolically in *Figure 2-4*, the energy balance can be stated as follows: the rate of energy entering with the stream at point 1 plus the rate of energy added as heat minus the rate of energy performing work and minus the rate of energy leaving at point 2 equals the rate of change of energy in the control volume. The mathematical expression for the energy balance is:

$$\dot{m}\!\left(h_1 + \frac{V_1^2}{2} + gz_1\right) + q - \dot{m}\!\left(h_2 + \frac{V_2^2}{2} + gz_2\right) - W = \frac{dE}{d\theta} \tag{2-1}$$

> *[Figure 2-4] Energy balance on a control volume experiencing steady flow rates.*

where:
- $\dot{m}$ = mass rate of flow, kg/s
- $h$ = enthalpy, J/kg
- $V$ = velocity, m/s
- $z$ = elevation, m
- $g$ = gravitational acceleration = 9.81 m/s²
- $q$ = rate of energy transfer in form of heat, W
- $W$ = rate of energy transfer in form of work, W
- $E$ = energy in system, J

Because we are limiting consideration to steady-flow processes, there is no change of $E$ with respect to time; the $dE/d\theta$ term is therefore zero, and the usual form of the steady-flow energy equation appears:

$$\dot{m}\!\left(h_1 + \frac{V_1^2}{2} + gz_1\right) + q = \dot{m}\!\left(h_2 + \frac{V_2^2}{2} + gz_2\right) + W \tag{2-2}$$

This form of the energy equation will be frequently used in the following chapters.

---

## 2-7 Heating and Cooling

In many heating and cooling processes, e.g., the water heater in Example 2-2 and the boiler in Example 2-3, the changes in certain of the energy terms are negligible. Often the magnitude of change in the kinetic-energy term $V^2/2$ and the potential-energy term $gz$ from one point to another is negligible compared with the magnitude of change of enthalpy, the work done, or heat transferred. If no work is done by a pump, compressor, or engine in the process, $W = 0$. The energy equation then reduces to:

$$q = \dot{m}(h_2 - h_1)$$

i.e., the rate of heat transfer equals the mass rate of flow multiplied by the change in enthalpy.

**Example 2-6** Water flowing at a steady rate of 1.2 kg/s is to be chilled from 10 to 4°C to supply a cooling coil in an air-conditioning system. Determine the necessary rate of heat transfer.

**Solution** From Table A-1, at 4°C $h = 16.80$ kJ/kg and at 10°C $h = 41.99$ kJ/kg. Then:

$$q = \dot{m}(h_2 - h_1) = (1.2\;\text{kg/s})(16.80 - 41.99) = -30.23\;\text{kW}$$

---

## 2-8 Adiabatic Processes

Adiabatic means that no heat is transferred; thus $q = 0$. Processes that are essentially adiabatic occur when the walls of the system are thermally insulated. Even when the walls are not insulated, if the throughput rates of energy are large in relation to the energy transmitted to or from the environment in the form of heat, the process may be considered adiabatic.

---

## 2-9 Compression Work

An example of a process which can be modeled as adiabatic is the compression of a gas. The change in kinetic and potential energies and the heat-transfer rate are usually negligible. After dropping out the kinetic- and potential-energy terms and the heat-transfer rate $q$ from Eq. (2-2) the result is:

$$W = \dot{m}(h_1 - h_2)$$

The power requirement equals the mass rate of flow multiplied by the change in enthalpy. The $W$ term is negative for a compressor and positive for an engine.

---

## 2-10 Isentropic Compression

Another tool is available to predict the change in enthalpy during a compression. If the compression is adiabatic and without friction, the compression occurs at constant entropy. On the skeleton pressure-enthalpy diagram of *Figure 2-5* such an ideal compression occurs along the constant-entropy line from 1 to 2.

The usefulness of this property is that if the entering condition to a compression (point 1) and the leaving pressure are known, point 2 can be located and the power predicted by computing $\dot{m}(h_1 - h_2)$. The actual compression usually takes place along a path to the right of the constant-entropy line (shown by the dashed line to point 2' in Figure 2-5), indicating slightly greater power than for the ideal compression.

> *[Figure 2-5] Pressure-enthalpy diagram showing a line of constant entropy.*

**Example 2-7** Compute the power required to compress 1.5 kg/s of saturated water vapor from a pressure of 34 kPa to one of 150 kPa.

**Solution** From Figure 2-2, at $p_1 = 34$ kPa and saturation:

$$h_1 = 2630\;\text{kJ/kg} \quad \text{and} \quad s_1 = 7.7\;\text{kJ/kg·K}$$

At $p_2 = 150$ kPa and $s_2 = s_1$:

$$h_2 = 2930\;\text{kJ/kg}$$

Then:

$$W = (1.5\;\text{kg/s})(2630 - 2930\;\text{kJ/kg}) = -450\;\text{kW}$$

---

## 2-11 Bernoulli's Equation

Bernoulli's equation is often derived from the mechanical behavior of fluids, but it is also derivable as a special case of the energy equation through second-law considerations. It can be shown that:

$$T\,ds = du + p\,dv \tag{2-3}$$

where $u$ is the internal energy in joules per kilogram. This expression is referred to as the Gibbs equation. For an adiabatic process $q = 0$, and with no mechanical work $W = 0$. Equation (2-2) then requires that:

$$h + \frac{V^2}{2} + gz = \text{const} \tag{2-4}$$

Differentiation yields:

$$dh + V\,dV + g\,dz = 0$$

The definition of enthalpy $h = u + pv$ can be differentiated to yield:

$$dh = du + p\,dv + v\,dp \tag{2-5}$$

Combining Eqs. (2-3) and (2-5) results in:

$$T\,ds = dh - v\,dp \tag{2-6}$$

Applying Eq. (2-6) to an isentropic process it follows that, since $ds = 0$:

$$dh = v\,dp = \frac{1}{\rho}\,dp$$

Substituting this expression for $dh$ into Eq. (2-4) for isentropic flow gives:

$$\frac{dp}{\rho} + V\,dV + g\,dz = 0 \tag{2-7}$$

For constant density Eq. (2-7) integrates to the Bernoulli equation:

$$\frac{p}{\rho} + \frac{V^2}{2} + gz = \text{const} \tag{2-8}$$

We shall use the Bernoulli equation for liquid and gas flows in which the density varies only slightly and may be treated as incompressible.

**Example 2-8** Water is pumped from a chiller in the basement, where $z_1 = 0$ m, to a cooling coil located on the twentieth floor of a building, where $z_2 = 80$ m. What is the minimum pressure rise the pump must be capable of providing if the temperature of the water is 4°C?

**Solution** Since the inlet and outlet velocities are equal, the change in the $V^2/2$ term is zero; so from Bernoulli's equation:

$$\frac{p_1}{\rho} + gz_1 = \frac{p_2}{\rho} + gz_2$$

The density $\rho = 1000$ kg/m³, and $g = 9.81$ m/s², therefore:

$$p_1 - p_2 = (1000\;\text{kg/m}^3)(9.81\;\text{m/s}^2)(80\;\text{m}) = 785\;\text{kPa}$$

---

## 2-12 Heat Transfer

Heat-transfer analysis is developed from the thermodynamic laws of conservation of mass and energy, the second law of thermodynamics, and three rate equations describing conduction, radiation, and convection. The rate equations were developed from the observation of the physical phenomena of energy exchange. They are the mathematical descriptions of the models derived to describe the observed phenomena.

Heat transfer through a solid material, referred to as **conduction**, involves energy exchange at the molecular level. **Radiation**, on the other hand, is a process that transports energy by way of photon propagation from one surface to another. Radiation can transmit energy across a vacuum and does not depend on any intervening medium to provide a link between the two surfaces. **Convection** heat transfer depends upon conduction from a solid surface to an adjacent fluid and the movement of the fluid along the surface or away from it. Thus each heat-transfer mechanism is quite distinct from the others; however, they all have common characteristics, as each depends on temperature and the physical dimensions of the objects considered.

---

## 2-13 Conduction

Observation of the physical phenomena and a series of reasoned steps establishes the rate equation for conduction. Consider the energy flux arising from conduction heat transfer along a solid rod. It is proportional to the temperature difference and the cross-sectional area and inversely proportional to the length. Fourier provided a mathematical model for this process. In a one-dimensional problem:

$$q = -kA\frac{\Delta t}{L} \tag{2-9}$$

where:
- $A$ = cross-sectional area, m²
- $\Delta t$ = temperature difference, K
- $L$ = length, m
- $k$ = thermal conductivity, W/m·K

The thermal conductivity is a characteristic of the material, and the ratio $k/L$ is referred to as the conductance.

The thermal conductivity, and thus the rate of conductive heat transfer, is related to the molecular structure of materials. The more closely packed, well-ordered molecules of a metal transfer energy more readily than the random and perhaps widely spaced molecules of nonmetallic materials. The free electrons in metals also contribute to a higher thermal conductivity. Thus good electric conductors usually have a high thermal conductivity.

**Table 2-1** Thermal conductivity of some materials

| Material | Temperature (°C) | Density (kg/m³) | Conductivity (W/m·K) |
|----------|:-:|:-:|:-:|
| Aluminum (pure) | 20 | 2707 | 204 |
| Copper (pure) | 20 | 8954 | 386 |
| Face brick | 20 | 2000 | 1.32 |
| Glass (window) | 20 | 2700 | 0.78 |
| Water | 21 | 997 | 0.604 |
| Wood (yellow pine) | 23 | 640 | 0.147 |
| Air | 27 | 1.177 | 0.026 |

The rate equation for conduction heat transfer is normally expressed in differential form:

$$q = -kA\frac{dt}{dx}$$

---

## 2-14 Radiation

Radiant-energy transfer results when photons emitted from one surface travel to other surfaces. Upon reaching the other surfaces radiated photons are either absorbed, reflected, or transmitted through the surface.

The energy radiated from a surface is defined in terms of its emissive power. It can be shown from thermodynamic reasoning that the emissive power is proportional to the fourth power of the absolute temperature. For a perfect radiator, generally referred to as a **blackbody**, the emissive power $E_b$ (W/m²) is:

$$E_b = \sigma T^4$$

where:
- $\sigma$ = Stefan-Boltzmann constant = $5.669 \times 10^{-8}$ W/m²·K⁴
- $T$ = absolute temperature, K

Since real bodies are not "black," they radiate less energy than a blackbody at the same temperature. The ratio of the actual emissive power $E$ (W/m²) to the blackbody emissive power is the **emissivity** $\varepsilon$:

$$\varepsilon = \frac{E}{E_b}$$

In many real materials the emissivity and absorptivity may be assumed to be approximately equal. These materials are referred to as **gray bodies**, and $\varepsilon = \alpha$ where $\alpha$ is the absorptivity (dimensionless).

Another important feature of radiant-energy exchange is that radiation leaving a surface is distributed uniformly in all directions. Therefore the geometric relationship between two surfaces affects the radiant-energy exchange between them. The geometric relationship can be determined and accounted for in terms of a shape factor $F_A$.

The optical characteristics of the surfaces also influence the rate of radiant heat transfer. If these effects are expressed by a factor $F_\varepsilon$, the radiant-energy exchange can be expressed as:

$$q = \sigma F_\varepsilon F_A A (T_1^4 - T_2^4) \tag{2-10}$$

---

## 2-15 Convection

The rate equation for convective heat transfer was originally proposed by Newton in 1701, from observation of physical phenomena:

$$q = h_c A (t_s - t_f) \tag{2-11}$$

where:
- $h_c$ = convection coefficient, W/m²·K
- $t_s$ = surface temperature, °C
- $t_f$ = fluid temperature, °C

This equation is widely used in engineering even though it is more a definition of $h_c$ than a phenomenological law for convection. In fact, the essence of convective heat-transfer analysis is the evaluation of $h_c$.

Dimensionless parameters provide the basis of most of the pertinent correlations:

$$\text{Reynolds number} \quad Re = \frac{\rho V D}{\mu}$$

$$\text{Prandtl number} \quad Pr = \frac{\mu c_p}{k}$$

$$\text{Nusselt number} \quad Nu = \frac{h_c D}{k}$$

Expressions have been developed for particular flow configurations so that the relationship can be expressed as:

$$Nu = C \cdot Re^n \cdot Pr^m$$

with values of the constant $C$ and the exponents $n$ and $m$ being determined experimentally.

> *[Figure 2-6] Typical data correlation for forced convection in smooth tubes, turbulent flow.*

**Table 2-2** Typical range of values of convective, boiling, and condensing heat-transfer coefficients

| Process | $h_c$ (W/m²·K) |
|---------|:-:|
| Free convection, air | 5–25 |
| Free convection, water | 20–100 |
| Forced convection, air | 10–200 |
| Forced convection, water | 50–10,000 |
| Boiling water | 3,000–100,000 |
| Condensing water | 5,000–100,000 |

---

## 2-16 Thermal Resistance

It is of interest that the rate equations for both conduction and convection are linear in the pertinent variables — conductance, area, and temperature difference. The radiation rate equation, however, is nonlinear in temperature. Heat-transfer calculations could be simplified greatly if the radiation heat transfer could be expressed in terms of a radiant conductance such that:

$$q = h_r A \Delta t$$

where $h_r$ is the equivalent heat-transfer coefficient by radiation, W/m²·K. When comparing with the Stefan-Boltzmann law, Eq. (2-10), $h_r$ can be expressed as:

$$h_r = \sigma F_\varepsilon F_A \frac{T_1^4 - T_2^4}{T_1 - T_2}$$

which is a nonlinear function of temperature. However, as the temperatures are absolute, $h_r$ does not vary greatly over modest temperature ranges and it is indeed possible to obtain acceptable accuracy in many cases using the linearized equation.

With the linearized radiation rate equation we have:

| Mode | Rate Equation |
|------|---------------|
| Conduction | $q = \frac{k}{L} A \Delta t$ |
| Convection | $q = h_c A \Delta t$ |
| Radiation | $q = h_r A \Delta t$ |

Noting that $q$ is a heat flow and $\Delta t$ is a potential difference, it is possible to draw an analogy with Ohm's law:

$$E = IR \quad \text{or} \quad I = \frac{E}{R}$$

When the heat-transfer equation is written according to the electrical analogy:

$$q = \frac{\Delta t}{R_T^*}$$

where $R_T^*$ is thermal resistance. For the three modes of heat transfer:

| Mode | $R_T^*$ |
|------|---------|
| Conduction | $\frac{L}{kA}$ |
| Convection | $\frac{1}{h_c A}$ |
| Radiation | $\frac{1}{h_r A}$ |

With these definitions of thermal resistance it is possible by analogy to apply certain concepts from circuit theory to heat transfer. Recall that the conductance $C$ is the reciprocal of the resistance, $C = 1/R_T^*$, and that in series circuits the resistances sum but for parallel circuits the conductances sum.

> *[Figure 2-7] Heat transfer from one room to another across a solid wall.*

> *[Figure 2-8] Heat-transfer circuit when the convective and radiative resistances are combined into a single surface resistance.*

In the transfer of energy from one room to another through a solid wall (Figure 2-7), the total resistance is:

$$R_{\text{tot}}^* = \frac{1}{C_{1r} + C_{1c}} + R_w^* + \frac{1}{C_{2r} + C_{2c}}$$

Convection and radiation occur simultaneously at a surface, and the convective and radiative conductances can be combined into a single conductance: $(h_c + h_r)A$. The combined surface conductance reduces the circuit to a series of resistances (Figure 2-8), where $R_s^* = 1/(h_c + h_r)A$.

Since the heat flux from one room to the other is constant at steady-state conditions:

$$q = \frac{t_1 - t_{s,1}}{R_{r\text{-}c,1}^*} = \frac{t_{s,1} - t_{s,2}}{R_w^*} = \frac{t_{s,2} - t_2}{R_{r\text{-}c,2}^*} = \frac{t_1 - t_2}{R_{\text{tot}}^*}$$

If $t_{s,1}$ is sought:

$$t_{s,1} = t_1 - \frac{R_{r\text{-}c,1}^*}{R_{\text{tot}}^*}(t_1 - t_2)$$

> *[Figure 2-9] Heat transfer through parallel paths.*

Another instance of parallel heat flow arises when structural elements are present in wall sections. In Figure 2-9, element C may be a structural member and the space between structural members is occupied by a different material, perhaps insulation. The total resistance is:

$$R_{\text{tot}}^* = R_{s,1}^* + R_A^* + \frac{R_B^* R_C^*}{R_B^* + R_C^*} + R_D^* + R_{s,2}^*$$

> *[Figure 2-10] Wall section in Example 2-9.*

**Example 2-9** Using the data given in Figure 2-10, determine the heat transfer in watts per square meter through the wall section and the temperature of the outside surface of the insulation if $t_o = 0°C$ and $t_i = 21°C$. In the insulated portion of the wall assume that 20 percent of the space is taken up with the structural elements, which are wood studs.

| Layer | $L$ (m) | $k$ (W/m·K) | $A$ (m²) | $R^*$ |
|-------|:---:|:---:|:---:|:---:|
| Outside air | — | — | 1.0 | 0.029 |
| Face brick | 0.09 | 1.30 | 1.0 | 0.070 |
| Air space | — | — | 1.0 | 0.170 |
| Sheathing | 0.013 | 0.056 | 1.0 | 0.232 |
| Insulation | 0.09 | 0.038 | 0.8 | 2.96 |
| Stud | 0.09 | 0.14 | 0.1 | 3.2 |
| Gypsum board | 0.013 | 0.16 | 1.0 | 0.08 |
| Inside air | — | — | 1.0 | 0.125 |

**Solution** From the data given, for each 1 m² of surface:

$$R_{\text{tot}}^* = 0.029 + 0.472 + \frac{2.96 \times 3.2}{2.96 + 3.2} + 0.08 + 0.125 = 2.24\;\text{K/W}$$

Thus:

$$q = \frac{t_i - t_o}{R_{\text{tot}}^*} = \frac{21 - 0}{2.24} = 9.37\;\text{W/m}^2$$

The temperature at the outside surface of the insulation is:

$$t_{\text{ins,o}} = 0°C + \frac{0.029 + 0.472}{2.24}(21 - 0°C) = 4.7°C$$

In Example 2-9, if the structural element had been neglected, the total resistance calculated would have been $R_{\text{tot}} = 3.67$ and $q$ would have been 5.73 W, which indicates that the presence of structural elements has a significant effect on the heat-transfer calculation.

### Overall Heat-Transfer Coefficient

The heat-transfer equation frequently appears in the form:

$$q = UA(t_i - t_o) \tag{2-12}$$

where $U$ = overall heat-transfer coefficient, W/m²·K, and $A$ = surface area, m².

Comparing with $q = \Delta t / R_{\text{tot}}^*$, we see that:

$$UA = \frac{1}{R_{\text{tot}}^*} \quad \text{and thus} \quad U = \frac{1}{(R_{\text{tot}}^*)A}$$

Many construction materials are available in standard thicknesses so that it is possible to present the resistance of the material directly. An additional convention is that resistances are expressed on the basis of 1 m². The relationship of these resistances $R$ (units of m²·K/W) to the $R^*$ resistances is:

$$R^* A = \frac{L}{k} = R \quad \text{(conduction)}$$

$$\frac{1}{h_c + h_r} = R_s \quad \text{(surface)}$$

For a plane wall for which $A$ is the same for all surfaces:

$$U = \frac{1}{R_{s,1} + R_w + R_{s,2}} = \frac{1}{\sum R}$$

Resistances presented in Chapter 4 (for example, in Table 4-3) will be the unstarred variety and have units of m²·K/W.

---

## 2-17 Cylindrical Cross Section

The previous discussion applies to plane geometries, but when heat is transferred through circular pipes, geometries are cylindrical. The area through which the heat flows is not constant, and a new expression for the resistance is required:

$$R_{\text{cyl}} = \frac{\ln(r_o / r_i)}{2\pi k l} \tag{2-13}$$

where:
- $r_o$ = outside radius, m
- $r_i$ = inside radius, m
- $l$ = length, m

---

## 2-18 Heat Exchangers

Heat exchangers are used extensively in air conditioning and refrigeration. A heat exchanger is a device in which energy is transferred from one fluid stream to another across a solid surface. Heat exchangers thus incorporate both convection and conduction heat transfer.

> *[Figure 2-11] Counterflow heat exchanger.*

The resistance concepts discussed in the previous sections prove useful in the analysis of heat exchangers as the first fluid, the solid wall, and the second fluid form a series thermal circuit:

$$q = \frac{\Delta t}{R_{\text{tot}}}$$

where:

$$R_{\text{tot}} = \frac{1}{h_1 A_1} + \frac{\ln(r_o / r_i)}{2\pi k l} + \frac{1}{h_2 A_2} \tag{2-14}$$

The subscripts 1 and 2 refer to fluids 1 and 2.

At a particular point in the heat exchanger the heat flux can be expressed by the thermal resistance and the temperature difference between the fluids. However, since the temperature of one or both fluids may vary as they flow through the heat exchanger, analysis is difficult unless a mean temperature difference can be determined. The usual practice is to use the **logarithmic-mean temperature difference (LMTD)** and a configuration factor:

$$\text{LMTD} = \frac{\Delta t_A - \Delta t_B}{\ln(\Delta t_A / \Delta t_B)} \tag{2-15}$$

where:
- $\Delta t_A$ = temperature difference between two fluids at position A, K
- $\Delta t_B$ = temperature difference between two fluids at position B, K

The analysis of heat exchangers will be examined at greater length in Chapter 12.

**Example 2-10** Determine the heat-transfer rate for the heat exchanger shown in Figure 2-11, given the following data: $h_1 = 50$ W/m²·K, $h_2 = 80$ W/m²·K, $t_{1,\text{in}} = 60°C$, $t_{1,\text{out}} = 40°C$, $t_{2,\text{in}} = 20°C$, $t_{2,\text{out}} = 30°C$, $r_o = 11$ mm, $r_i = 10$ mm, length = 1 m, and for the metal $k = 386$ W/m·K.

**Solution**

$$A_1 = 2\pi r_o l = 0.069\;\text{m}^2 \quad A_2 = 0.063\;\text{m}^2$$

$$R_{\text{tot}} = \frac{1}{0.069 \times 50} + \frac{\ln(11/10)}{2\pi(1)(386)} + \frac{1}{0.063 \times 80} = 0.487\;\text{W/K}$$

$$\text{LMTD} = \frac{(60 - 30) - (40 - 20)}{\ln(30/20)} = 24.7°C$$

$$q = \frac{24.7}{0.487} = 50.7\;\text{W}$$

---

## 2-19 Heat-Transfer Processes Used by the Human Body

The primary objective of air conditioning is to provide comfortable conditions for people. From the thermal standpoint the body is an inefficient machine but a remarkably good regulator of its own temperature. The human body receives fuel in the form of food, converts a fraction of the energy in the fuel into work, and rejects the remainder as heat. It is the continuous process of heat rejection which requires a thermal balance.

> *[Figure 2-12] The body as a heat generator and rejector.*

In a steady-state heat balance the heat energy produced by metabolism equals the rate of heat transferred from the body by convection, radiation, evaporation, and respiration. The complete equation for the heat balance becomes:

$$M = \mathscr{E} \pm \mathscr{R} \pm C + B \pm S \tag{2-16}$$

where:
- $M$ = metabolism rate, W
- $\mathscr{E}$ = heat loss by evaporation, W
- $\mathscr{R}$ = rate of heat transfer by radiation, W
- $C$ = rate of heat transfer by convection, W
- $B$ = heat loss by respiration, W
- $S$ = rate of change of heat storage in body, W

Several of the terms on the right side of Eq. (2-16) always represent losses of heat from the body, while the radiation, convection, and thermal-storage terms can either be plus or minus.

---

## 2-20 Metabolism

Metabolism is the process which the body uses to convert energy in food into heat and work. A person can convert food energy into work with an efficiency as high as 15 to 20 percent for short periods. In nonindustrial applications, particularly during light activity, the efficiency of conversion into work is of the order of 1 percent. The basal metabolic rate is the average possible rate, which occurs when the body is at rest, but not asleep.

We have several interests in the metabolism rate: (1) it is the $M$ term in the heat-balance equation (2-16) that must be rejected from the body through the various mechanisms; (2) this heat contributes to the cooling load of the air-conditioning system. The heat-rejection rate by an occupant in a conditioned space may vary from 120 W for sedentary activities to more than 440 W for vigorous activity.

**Example 2-11** For a rough estimate, consider the body as a heat machine assuming an intake in the form of food of 2400 cal/d (1 cal = 4.19 J). If all intake is oxidized and is rejected in the form of heat, what is the average heat release in watts?

**Solution** The average heat release is calculated to be 0.12 W, which disagrees with the expected quantity of 120 W by a factor of 1000. The explanation is that calories used in measuring food intake are large calories or kilogram calories, in contrast to the gram calories which make up 4.19 J. So indeed the average heat release is about 120 W.

---

## 2-21 Convection

The $C$ term in Eq. (2-16) represents the rate of heat transfer due to air flow convecting heat to or from the body. The elementary equation for convection applies:

$$C = h_c A (t_s - t_a) \tag{2-17}$$

where:
- $A$ = body surface area, m²
- $t_s$ = skin or clothing temperature, °C
- $t_a$ = air temperature, °C

The surface area of the human body is usually in the range of 1.5 to 2.5 m², depending upon the size of the person. The heat-transfer coefficient $h_c$ depends upon the air velocity across the body. An approximate value of $h_c$ during forced convection can be computed from:

$$h_c = 13.5 V^{0.6} \tag{2-18}$$

where $V$ is the air velocity in meters per second.

The skin temperature is controllable to a certain extent by the temperature-regulating mechanism of the body and generally ranges between 31 and 33°C for those parts of the body covered by clothing.

---

## 2-22 Radiation

The equation for heat transfer between the human body and its surroundings has already appeared as Eq. (2-10). Not all parts of the body radiate to the surroundings; some radiate to other parts of the body. The effective area of the body for radiation is consequently less than the total surface area, usually about 70 percent of the total.

The emissivity of the skin and clothing is very close to that of a blackbody and thus has a value of nearly 1.0. The temperature to which the body radiates is often referred to as the **mean radiant temperature**, a fictitious uniform temperature of the complete enclosure that duplicates the rate of radiant heat flow of the actual enclosure.

---

## 2-23 Evaporation

Removal of heat from the body by evaporation of water from the skin is a major means of heat rejection. The transfer of heat between the body and the environment by convection and radiation may be either toward the body or away from it, depending upon the ambient conditions. Evaporation, on the other hand, always constitutes a rejection of heat from the body. In hot environments, sweating provides the dominant method of heat removal from the body.

> *[Figure 2-13] Heat rejection by nonsweating (insensible) evaporation and by sweating.*

There are two modes by which the body wets the skin: **diffusion** and **sweating**. Diffusion, or insensible evaporation, is a constant process, while sweating is controlled by the thermoregulatory system. The rate of heat transfer by insensible evaporation is:

$$q_{\text{ins}} = h_{fg} A C_{\text{diff}} (p_s - p_a) \tag{2-19}$$

where:
- $q_{\text{ins}}$ = rate of heat transfer by insensible evaporation, W
- $h_{fg}$ = latent heat of water, J/kg
- $A$ = area of body, m²
- $C_{\text{diff}}$ = coefficient of diffusion, kg/Pa·s·m²
- $p_s$ = vapor pressure of water at skin temperature, Pa
- $p_a$ = vapor pressure of water vapor in ambient air, Pa

The dominant mechanism for rejecting large rates of heat from the body is by sensible sweating and subsequent evaporation of this sweat. Maximum rates of sweating, at least for short periods of time, are of the order of 0.3 g/s, so if all this sweat evaporates and removes 2430 kJ/kg, the potential heat removal rate by sweating is approximately 700 to 800 W.

---

## Problems

**2-1** Water at 120°C and a pressure of 250 kPa passes through a pressure-reducing valve and then flows to a separating tank at standard atmospheric pressure of 101.3 kPa, as shown in *Figure 2-14*.

> *[Figure 2-14] Pressure-reducing valve in Problem 2-1.*

(a) What is the state of the water entering the valve (subcooled liquid, saturated liquid, or vapor)?

(b) For each kilogram that enters the pressure-reducing valve, how much leaves the separating tank as vapor? *Ans. 0.0375*

**2-2** Air flowing at a rate of 2.5 kg/s is heated in a heat exchanger from −10 to 30°C. What is the rate of heat transfer? *Ans. 100 kW*

**2-3** One instrument for measuring the rate of airflow is a venturi, as shown in *Figure 2-15*, where the cross-sectional area is reduced and the pressure difference between positions A and B measured. The flow rate of air having a density of 1.15 kg/m³ is to be measured in a venturi where the area at position A is 0.5 m² and the area at B is 0.4 m². The deflection of water (density = 1000 kg/m³) in a manometer is 20 mm. The flow between A and B can be considered to be frictionless so that Bernoulli's equation applies.

> *[Figure 2-15] A venturi for measuring air flow.*

(a) What is the pressure difference between positions A and B?

(b) What is the airflow rate? *Ans. 12.32 m³/s*

**2-4** Use the perfect-gas equation with $R = 462$ J/kg·K to compute the specific volume of saturated vapor water at 20°C. Compare with data of Table A-1. *Ans. Deviation = 0.19%*

**2-5** Using the relationship shown on Figure 2-6 for heat transfer when a fluid flows inside a tube, what is the percentage increase or decrease in the convection heat-transfer coefficient $h_c$ if the viscosity of the fluid is decreased 10 percent? *Ans. 4.3% increase*

**2-6** What is the order of magnitude of heat release by convection from a human body when the air velocity is 0.25 m/s and its temperature is 24°C? *Ans. 60 W*

**2-7** What is the order of magnitude of radiant heat transfer from a human body in a comfort air-conditioning situation? *Ans. 40 W*

**2-8** What is the approximate rate of heat loss due to insensible evaporation if the skin temperature is 32°C, the vapor pressure is 4150 Pa, and the vapor pressure of air is 1700 Pa? The latent heat of water is 2.43 MJ/kg; $C_{\text{diff}} = 1.2 \times 10^{-9}$ kg/Pa·s·m². *Ans. 18 W*

---

## References

1. G. J. Van Wylen and R. E. Sonntag: "Fundamentals of Classical Thermodynamics," Wiley, New York, 1978.
2. W. D. Reynolds and H. C. Perkins: "Engineering Thermodynamics," McGraw-Hill, New York, 1970.
3. K. Wark: "Thermodynamics," 2d ed., McGraw-Hill, New York, 1976.
4. J. P. Holman: "Heat Transfer," 4th ed., McGraw-Hill, New York, 1976.
5. F. Kreith and W. Z. Black: "Basic Heat Transfer," Harper & Row, New York, 1980.
6. "ASHRAE Handbook, Fundamentals Volume," chap. 8, American Society of Heating, Refrigerating, and Air Conditioning Engineers, Atlanta, Ga., 1981.
