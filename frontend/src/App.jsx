import { useState } from "react";


const API_BASE_URL = "/api";


function App() {

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  async function askKonnect() {

    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);


    try {

      const response = await fetch(
        `${API_BASE_URL}/query`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            question: question.trim()
          })
        }
      );


      if (!response.ok) {

        const errorData =
          await response.json();

        throw new Error(
          errorData.detail ||
          "KONNECT request failed."
        );
      }


      const data =
        await response.json();


      setAnswer(data.answer || "");

      setSources(
        data.sources || []
      );

    }
    catch (err) {

      setError(
        err.message ||
        "Unable to connect to KONNECT."
      );

    }
    finally {

      setLoading(false);

    }
  }


  function handleKeyDown(event) {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      askKonnect();

    }
  }


  function getDocumentUrl(source) {

    const encodedPath =
      encodeURIComponent(
        source.source.replace(
          /^data[\\/]/,
          ""
        )
      );

    return `/api/documents/${encodedPath}`;
  }


  return (

    <div className="app">

      <header className="header">

        <div>

          <h1>KONNECT</h1>

          <p>
            Technical Troubleshooting Assistant
          </p>

        </div>

        <div className="status">
          ● Online
        </div>

      </header>


      <main className="container">

        <section className="hero">

          <h2>
            Ask KONNECT
          </h2>

          <p>
            Search technical knowledge,
            incidents and troubleshooting
            information using natural language.
          </p>


          <div className="query-box">

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Example: What causes application connectivity failures?"
              rows="4"
            />


            <button
              onClick={askKonnect}
              disabled={
                loading ||
                !question.trim()
              }
            >

              {loading
                ? "Thinking..."
                : "Ask KONNECT"}

            </button>

          </div>

        </section>


        {error && (

          <section className="error-card">

            <strong>
              Request failed
            </strong>

            <p>
              {error}
            </p>

          </section>

        )}


        {answer && (

          <section className="answer-card">

            <div className="section-title">
              Answer
            </div>

            <div className="answer">

              {answer}

            </div>

          </section>

        )}


        {sources.length > 0 && (

          <section className="sources-card">

            <div className="section-title">
              Sources
            </div>


            <div className="sources">

              {sources.map(
                (source, index) => (

                  <a
                    key={`${source.source}-${index}`}
                    className="source"
                    href={getDocumentUrl(source)}
                    target="_blank"
                    rel="noreferrer"
                  >

                    <div>

                      <strong>
                        📄 {source.file_name}
                      </strong>

                      <span>
                        Chunk {source.chunk_id}
                      </span>

                    </div>

                    <span className="open">
                      Open →
                    </span>

                  </a>

                )
              )}

            </div>

          </section>

        )}

      </main>


      <footer>

        KONNECT • AI-powered
        technical troubleshooting

      </footer>

    </div>

  );
}


export default App;