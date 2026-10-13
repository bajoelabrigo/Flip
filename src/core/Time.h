#pragma once

#include <cstdint>

namespace drift {

using TimeUs = int64_t;

constexpr TimeUs kUsPerSecond = 1'000'000;
constexpr TimeUs kUsPerMs = 1'000;

// Rounded, not truncated: QML hands over times in double seconds, and a clip dropped exactly
// against its neighbour's edge (1.2 s is 1199999.99... us) used to land 1 us inside it, so the
// overlap check pushed it past the neighbour as if the drop had been refused.
constexpr TimeUs secondsToUs(double seconds)
{
    const double us = seconds * static_cast<double>(kUsPerSecond);
    return static_cast<TimeUs>(us >= 0.0 ? us + 0.5 : us - 0.5);
}

constexpr double usToSeconds(TimeUs us)
{
    return static_cast<double>(us) / static_cast<double>(kUsPerSecond);
}

constexpr TimeUs frameDurationUs(int fps)
{
    return fps > 0 ? kUsPerSecond / fps : kUsPerSecond / 30;
}

} // namespace drift
