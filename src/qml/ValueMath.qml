pragma Singleton
import QtQuick

// Arithmetic in value fields, as After Effects reads them (0.30): "100+20" or "(1920-133)/2" give the result;
// starting with an operator ("+50", "*2", "/2", or "+=", "-=", "*=", "/=") works on the value already there.
// A lone leading "-" stays a negative number. A small parser of its own: nothing typed is ever run as code.
QtObject {
    // The number `text` means given the field's `current` value, or NaN when it is not a sum.
    function evaluate(text, current) {
        let s = String(text).trim().replace(/,/g, ".").replace(/×/g, "*").replace(/÷/g, "/")
        if (s.length === 0)
            return NaN
        let relative = ""
        const assign = /^([+\-*/])=/.exec(s)
        if (assign) {
            relative = assign[1]
            s = s.slice(2)
        } else if (/^[+*/]/.test(s)) {
            relative = s[0]
            s = s.slice(1)
        }
        const v = parse(s)
        if (isNaN(v))
            return NaN
        const base = Number(current)
        switch (relative) {
        case "+": return base + v
        case "-": return base - v
        case "*": return base * v
        case "/": return v === 0 ? NaN : base / v
        }
        return v
    }

    // expr := term (("+" | "-") term)* ; term := factor (("*" | "/") factor)* ;
    // factor := ("+" | "-") factor | number | "(" expr ")"
    function parse(s) {
        const src = s.replace(/\s+/g, "")
        let i = 0
        function number() {
            const m = /^(\d+\.?\d*|\.\d+)(e[+\-]?\d+)?/i.exec(src.slice(i))
            if (!m)
                return NaN
            i += m[0].length
            return parseFloat(m[0])
        }
        function factor() {
            if (src[i] === "+") { ++i; return factor() }
            if (src[i] === "-") { ++i; return -factor() }
            if (src[i] === "(") {
                ++i
                const v = expr()
                if (src[i] !== ")")
                    return NaN
                ++i
                return v
            }
            return number()
        }
        function term() {
            let v = factor()
            while (i < src.length && (src[i] === "*" || src[i] === "/")) {
                const op = src[i++]
                const r = factor()
                v = op === "*" ? v * r : (r === 0 ? NaN : v / r)
            }
            return v
        }
        function expr() {
            let v = term()
            while (i < src.length && (src[i] === "+" || src[i] === "-")) {
                const op = src[i++]
                const r = term()
                v = op === "+" ? v + r : v - r
            }
            return v
        }
        const v = expr()
        return i === src.length && isFinite(v) ? v : NaN
    }
}
