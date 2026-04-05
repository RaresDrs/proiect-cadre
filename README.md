BeamWise 2D
Professional Structural Analysis & FEM Engine
BeamWise 2D is a high-performance web-based application designed for the structural analysis of 2D frames and beams. Built with Python and powered by the Finite Element Method (FEM), it provides engineers and students with an intuitive interface to calculate internal forces and deformations in real-time.

🚀 Key Features
Advanced FEM Solver: Precise calculation of nodal displacements, reactions, and member forces.

Interactive UI: Modern dashboard built with Streamlit for seamless user experience.

Visual Force Diagrams: High-quality rendering of:

M - Bending Moment Diagrams

V - Shear Force Diagrams

N - Axial Force Diagrams

Flexible Loading: Support for point loads (via magnitude/angle or components) and distributed loads.

Dual-Notation Input: Switch between Global Coordinates and Component-based force input.

Professional Reporting:Export results and diagrams directly to PDF.

🛠️ Tech Stack
Language: Python 3.10+

Framework: Streamlit

Math & Physics: NumPy

Visualization: Matplotlib
 How it Works The engine discretizes the structure into beam elements.
 Each element's stiffness matrix is assembled into a global matrix, solving for displacements using:
 [K] * {u} = {F}
 Where:
 [K] = Global Stiffness Matrix
 {u}= Nodal Displacement Vector
 {F} = Applied Load Vector
 ⚠️ Disclaimer This software is intended for educational and preliminary design check purposes only.
 All final engineering calculations must be verified by a certified professional engineer according to local building codes.
 AuthorRares - Civil Engineering Student & Developer
 GitHub: @RaresDrs
