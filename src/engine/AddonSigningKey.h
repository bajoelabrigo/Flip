#pragma once

#include <array>
#include <cstdint>

// Trust root for .driftpkg addon packages: Flip Studio's own key (Drift's packs are signed with
// CutWire's and are not ours to install). The matching Ed25519 private key never ships and is not
// in any repository; packages are built and signed with driftpkg.py in bajoelabrigo/flip-addons.
// Rotating it means shipping a new binary, so treat this array as an ABI.

namespace drift::addon {

inline constexpr std::array<std::uint8_t, 32> kSigningPublicKey = {
    0x6a, 0xa5, 0x89, 0xa4, 0xd3, 0x65, 0x57, 0xb6, 0x51, 0x47, 0xc4,
    0x12, 0x93, 0x52, 0x5f, 0xc2, 0x02, 0x11, 0xda, 0xcf, 0xf4, 0x15,
    0xe2, 0xdf, 0x02, 0x44, 0x57, 0xd0, 0x79, 0xd6, 0xa4, 0x64,
};

} // namespace drift::addon
