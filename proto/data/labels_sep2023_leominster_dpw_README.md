# Leominster DPW flash-flood damage, 11-12 Sept 2023

54 damage points from the City of Leominster Department of Public Works GIS layer `FlashFloodDamage` (all flagged eligible for
federal aid), provided by J. Roseberry, PLS (Leominster DPW) to M. Eldokla on 22 Oct 2026 for research. Types: edge washouts (35),
road / storm-drain / gutter / sidewalk washouts, headwall damage, debris. Coordinates exact (surveyed points, reprojected from
NAD83(2011) MA Mainland ftUS to WGS84). Times: storm day only.

Mapping of `Type_of_Da` to label type: anything with "wash" -> washout; culvert/headwall -> culvert_failure; else other_damage.
The `road` column holds the DPW's abbreviated location code (e.g. `wa`, `lit`, `plS`), not a full street name.

Closure durations reported by the DPW (email, 22 Oct 2026): Pleasant St @ Colburn St 2 weeks; Lancaster St @ Malburn St 1 week;
Hamilton St near Main St 1 week; Mechanic St @ Manning Ave 1 week. Many smaller washouts narrowed roads to one lane, some for 2 months.

The city's storm-drain network (also provided) is NOT stored in this public repository.
