// Conjugation worksheet, or its answer key. Rendered by hegram.pdf.render_pdf, which passes the questions
// as JSON in sys.inputs.data:
//   {"answers": bool, "questions": [{"segments": [{"text", "highlight"}], "ref": str,
//                                    "fields": [{"label", "value", "hebrew"}]}]}
#let data = json(bytes(sys.inputs.data))

// Latin text in Arial; Liberation Sans and Arimo are its metric-compatible stand-ins on Linux.
#let latin = ("Arial", "Liberation Sans", "Arimo")
#let hebrew = "Ezra SIL"

#set document(title: if data.answers { "Corrigé de conjugaison" } else { "Exercice de conjugaison" })
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.6cm), numbering: "1 / 1")
#set text(font: latin, size: 10pt, lang: "fr")

#let verse(segments) = text(font: hebrew, size: 15pt, lang: "he", dir: rtl)[
  #for s in segments {
    if s.highlight { highlight(fill: rgb("#bfdbfe"), extent: 1pt, s.text) } else { s.text }
  }
]

#let field(f) = {
  [#f.label : ]
  if data.answers {
    if f.hebrew { text(font: hebrew, size: 13pt, f.value) } else { strong(f.value) }
  } else {
    box(width: 1fr, stroke: (bottom: 0.5pt + gray), height: 1em)
  }
}

#align(center, text(size: 14pt, weight: "bold")[
  #if data.answers [Corrigé — exercice de conjugaison] else [Exercice de conjugaison]
])
#v(0.6em)

#for (i, q) in data.questions.enumerate(start: 1) {
  block(breakable: false, width: 100%, inset: (y: 0.7em), stroke: (bottom: 0.5pt + luma(220)))[
    #grid(
      columns: (1fr, auto),
      column-gutter: 0.8em,
      align: (right, right + top),
      verse(q.segments), text(font: hebrew, size: 13pt, numbering("א", i)),
    )
    #text(size: 8pt, style: "italic", fill: luma(90), q.ref)
    #v(0.2em)
    #grid(columns: (1fr,) * 4, column-gutter: 1.2em, ..q.fields.map(field))
  ]
}
