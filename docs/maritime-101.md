# Maritime 101 — Plain English for the Team

None of us come from shipping. This page explains every shipping word we use, without jargon. Read it once and the rest of the docs will make sense.

## The whole project in 30 seconds

- Most of the world's goods travel on big ships.
- The **Suez Canal** is a man-made waterway through Egypt that connects Europe and Asia. Without it, ships would have to sail all the way around Africa, which adds about 1–2 weeks.
- **Port Said** is the city at the canal's northern end, on the Mediterranean.
- A ship arriving at Port Said usually **can't go straight in**. It has to wait its turn, either:
  - for the **canal**: ships go through in scheduled groups, like buses leaving at fixed times, or
  - for a **free spot at the dock** to load or unload cargo.
- While it waits, the ship parks at sea in a marked area called the **anchorage**. Think of it as a **parking lot on the water**: the ship drops its anchor and sits there.
- **Waiting is expensive.** The ship's owner or renter pays daily fees, crew salaries, and fuel, and the cargo arrives late.
- **Our job:** predict how crowded that sea parking lot will be, and how long a ship arriving *now* will wait, 6–24 hours ahead.

## How we "see" ships: AIS

- Every large ship must carry an **AIS transponder**, a box that keeps broadcasting by radio: *who I am, where I am, how fast I'm going, which way*.
- Picture every ship constantly shouting its GPS location, like the car dots in the Uber app.
- The radio signal only travels as far as the horizon, so **height is everything**. An antenna 15 m up hears ships ~28–37 km away; 20 m up, ~46 km; a hilltop or tower can reach 75–110 km. Antennas on the coast, and satellites, pick it up.
- Services like **aisstream.io** collect what volunteer antennas hear and stream it to us.
- **Our test (Oct 6, 2026):** no antenna near Egypt feeds aisstream, so we hear nothing from Egyptian waters. It's like a radio that can't pick up the station.

## The vocabulary

### Ships and their IDs

| Word | Plain meaning |
|---|---|
| Vessel | Ship. Same thing. |
| MMSI | The ship's radio ID number (9 digits). Like a phone number. **Our main key for each ship.** |
| IMO number | A permanent ID for the ship itself (7 digits). Never changes, like a car's chassis number. |
| Call sign | The ship's radio nickname, like a username. |
| Class A / Class B | Two kinds of AIS box. **Class A** is required on big commercial ships, which is what we care about. **Class B** is a cheaper version on yachts and small boats, which is noise for us. |
| Ship type | A number code for the kind of ship. 70–79 = cargo ship, 80–89 = tanker, 60s = passenger, 52 = tug, 37 = yacht. |
| Container ship | Carries the big metal boxes (containers) you see on trucks. |
| Tanker | Carries liquids: oil, gas, chemicals. |
| Bulk carrier | Carries loose cargo poured into the hold: grain, coal, iron ore. |
| Tug | A small, powerful boat that pushes or pulls big ships into position. |

### Movement (what the ship's dot tells us)

| Word | Plain meaning |
|---|---|
| Latitude / longitude | GPS coordinates (north-south / east-west position). |
| Speed over ground (SOG) | The speedometer. Measured in **knots**: 1 knot ≈ 1.85 km/h. A ship at sea does ~10–20 knots; a parked ship shows ~0. |
| Course over ground (COG) | The direction the ship is actually moving (0° = north, 90° = east, 180° = south, 270° = west). |
| Heading | The direction the ship's nose points. It can differ from the course because wind and current push ships sideways. |
| Rate of turn | How fast it's turning. We don't need it. |
| Navigational status | A status **the crew sets by hand**: "moving with engine", "at anchor", "tied to the dock". Like a WhatsApp status that people forget to update. In our data, **58% of ships saying "moving" weren't moving.** |
| Nautical mile | Distance at sea. 1 nautical mile = 1.85 km. |

### Places

| Word | Plain meaning |
|---|---|
| Port | A place where ships load and unload. Egypt's main Mediterranean ports are Alexandria, Damietta, and Port Said. |
| Berth | One parking spot at the dock where a ship ties up. Like a gate at an airport. |
| Terminal | A section of a port run by one company, with its own cranes and berths. |
| Anchorage | **The sea parking lot** where ships wait. |
| Anchored vs. moored | **Anchored** = parked at sea using the anchor (waiting). **Moored** = tied to the dock (being served). |
| Convoy | A group of ships that go through the canal together at a scheduled time. The canal is too narrow in parts for free two-way traffic. |
| Chokepoint / gateway | A narrow spot all traffic has to squeeze through (the Suez Canal, the Strait of Hormuz…). |

### Trip information (typed in by the crew)

| Word | Plain meaning |
|---|---|
| Destination | Where the ship says it's going. Free text and messy: "LIMASSOL" and "CYLMS" are the same port written two ways. |
| ETA | **Estimated Time of Arrival**: when the ship expects to arrive. The crew types it in and often never updates it. **79% of the ETAs we saw were already in the past.** |
| Draught (draft) | How deep the ship sits in the water. Deep = full of cargo; shallow = empty. |
| Dimensions | The ship's length and width in meters. |

### Money and the people involved (who might pay us)

| Word | Plain meaning |
|---|---|
| Shipping line / carrier | A company that runs ships (Maersk, MSC…). Like an airline, but for cargo. |
| Shipping agent | The ship's local helper at the port: paperwork, booking pilots, ordering supplies. **Likely our first customers.** |
| Freight forwarder | Organizes transport for a company's goods (books the ship, the truck, the warehouse). A travel agent for cargo. |
| Terminal operator | The company that runs the docks and cranes. |
| Charter | Renting a ship. |
| Laytime | The time the rental contract allows for loading and unloading. |
| **Demurrage** | **The late fee** when a ship stays longer than the contract allows. Paid per day, and it can be large. (Cite a source before putting a number in the deck.) |
| Detention | A late fee for keeping the containers (the boxes) too long. |
| Bunkering / bunkers | Refueling a ship / ship fuel. Port Said is a big refueling stop. |
| Ship chandler | A business selling supplies (food, water, ropes) to ships. |
| Pilot | A local expert captain who boards to steer the ship into the port or canal. |
| Turnaround time | Total time from arriving at a port to leaving it. |

### Data words

| Word | Plain meaning |
|---|---|
| Position report | The message saying "here's where I am right now". In our data it arrives about once a minute per ship. |
| Static data | The message saying "here's who I am": name, type, size, destination, ETA. Sent about every 6 minutes. |
| "Not available" codes | AIS uses fake numbers to mean "I don't know": speed **102.3**, heading **511**, course **360**, latitude **91** / longitude **181**. Treat them as empty, never as real values. |
| IMF PortWatch | A free website from the International Monetary Fund that counts ships passing through the canal each day (~40/day). **Our answer key** for checking our own counts. |
| Bounding box | The rectangle on the map we subscribe to. "Send me every ship inside this box." |

## What we predict, exactly

> Looking at the sea parking lot at Port Said: **in 6, 12 and 24 hours, how many ships will be waiting, and how long will a ship arriving now have to wait?**

**How we get the right answers to train on**, without any official port records:
1. Watch each ship's dot.
2. When the dot **stops inside the parking lot**, the clock starts.
3. When it **starts moving toward the canal or the dock**, the clock stops.
4. The difference is that ship's **waiting time**.

We judge ships by **how they move** (speed + location), not by what the crew typed, because the typed fields are unreliable.

## Where our data comes from (decided 2026-10-07)

The free live feed (aisstream.io) can't hear Egypt; its antennas are in Turkey, Cyprus and Israel. We chose **free sources only** (no paid data, no hardware):

- **Port Said and the Suez Canal: Global Fishing Watch.** Satellites pick up every ship's AIS signal. We get one position per ship per hour, going back years, but about **5 days late**.
  - That's perfect for **teaching and testing** the model. We proved it shows the 2021 Ever Given queue: about 15 waiting ships normally, **160** at the peak.
  - It can't power live predictions, so the Port Said demo **replays** real past data.
- **Alexandria: the Port Authority's public ship board.** Live and official: which ships are expected, which are in port (with arrival and docking times), and which have left. We record it every 30 minutes.
  - It has no history, so we also learn from Global Fishing Watch's Alexandria data.
  - After 4–6 weeks of collecting both side by side, Alexandria gets **live** predictions.
- **For checking our numbers:** IMF PortWatch (daily ship counts) and the Suez Canal Authority (official monthly totals).

Options we considered and set aside: building our own antenna (~$100, Alexandria only) and paying a data company (~€15–80/month). Either one would add live Port Said data later, with no other changes to the pipeline.
