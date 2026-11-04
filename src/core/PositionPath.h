#pragma once

#include "Clip.h"

namespace drift {

// After Effects' joined Position (0.30, Jorge: «que la línea de tiempo funcione como After
// Effects»). X and Y stay two tracks, so everything that reads a clip's place keeps working, but
// their keys carry one path: a curve in space with its own handles (dragged on the motion path in
// the preview) and, apart from it, the timing as the distance travelled along that curve (the speed
// graph). Bending the path no longer changes the speed, nor the other way round, and between two
// keys the clip moves at an even speed unless the timing is eased. See Keyframe::spatial.

// Two or more keys on X or Y: Position moves.
bool positionAnimated(const Clip &clip);

// Puts both axes on the same key times, gives the timing and the Auto Bezier handles from X's keys
// (or Y's where only Y has one) to both, and works out the distances along the path. Idempotent;
// on a clip whose Position is separate it only drops what keys pasted from a joined one carried.
void syncJoinedPosition(Clip &clip);

// Separate dimensions off and on. Joining keeps the path's shape roughly (the value handles become
// Auto Bezier) and the eases; separating turns the spatial handles back into value ones.
void joinPosition(Clip &clip);
void separatePosition(Clip &clip);

// How far along the path the clip is at `relative` (clip time): what the speed graph draws.
double pathDistanceAt(const Clip &clip, TimeUs relative);

} // namespace drift
