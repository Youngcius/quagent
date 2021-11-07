"""
EPs & SPDs routing
---
Align resource of EPs and SPDs for users, that is, this module is in charge of controlling the 5x16 & 8x8 switches.
5x16 switch: five 1*16 sub-switch. 1 input: one kind of entangled photon; 16 output: 16 different users.
8x8 switch: eight 1*8 sub-switch. 1 output: one set of SNSPD; 8 input: 8 different users.
"""