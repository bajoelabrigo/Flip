pragma Singleton
import QtQml

// What happened once in this run of the app and must not happen again until the next one.
QtObject {
    // The Stock sign-in popup (0.32) opens by itself the first time Stock is shown signed out.
    property bool stockSignInOffered: false
}
