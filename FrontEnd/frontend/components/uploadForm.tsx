"use client";

import { useRef, useState } from "react";

type AuditResult = {
  risk_score: number;
  risk_level: string;
  findings: unknown[];
  patches?: unknown[];
};

type UploadFormProps = {
  onResult?: (result: AuditResult) => void;
};


export default function UploadForm({
  onResult,
}: UploadFormProps) {

  const [contract, setContract] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const [error, setError] = useState("");

  const fileInputRef =
    useRef<HTMLInputElement>(null);


  const MAX_FILE_SIZE =
    1 * 1024 * 1024;


  async function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {

    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setError("");


    // -------------------------------
    // Validate file extension
    // -------------------------------

    if (!file.name.endsWith(".sol")) {

      setError(
        "Please upload a Solidity (.sol) file."
      );

      event.target.value = "";

      return;
    }


    // -------------------------------
    // Validate file size
    // -------------------------------

    if (file.size > MAX_FILE_SIZE) {

      setError(
        "File must be smaller than 1 MB."
      );

      event.target.value = "";

      return;
    }


    try {

      // Read file as plain text
      const fileContent =
        await file.text();


      // Basic validation
      if (!fileContent.trim()) {

        setError(
          "The uploaded contract is empty."
        );

        return;
      }


      // Put Solidity code into textarea
      setContract(fileContent);

    } catch {

      setError(
        "Could not read the uploaded file."
      );

    }
  }


  async function handleSubmit(
    event: React.FormEvent
  ) {

    event.preventDefault();

    setError("");


    // -------------------------------
    // Validate contract
    // -------------------------------

    if (!contract.trim()) {

      setError(
        "Please paste or upload a Solidity contract."
      );

      return;
    }


    // Maximum 1 MB
    const contractSize =
      new TextEncoder().encode(contract).length;

    if (contractSize > MAX_FILE_SIZE) {

      setError(
        "Contract must be smaller than 1 MB."
      );

      return;
    }


    setIsLoading(true);


    try {

      const response = await fetch(
        "http://127.0.0.1:8000/audit/",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            contract: contract,
          }),
        }
      );


      const data =
        await response.json();


      // -------------------------------
      // Handle API errors
      // -------------------------------

      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Contract analysis failed."
        );

      }


      // Send result to parent component
      if (onResult) {
        onResult(data);
      }


      console.log(
        "Audit result:",
        data
      );


    } catch (error) {

      if (error instanceof Error) {

        setError(error.message);

      } else {

        setError(
          "Something went wrong while analyzing the contract."
        );

      }

    } finally {

      setIsLoading(false);

    }
  }


  function handleNewScan() {

    setContract("");

    setError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }


  return (

    <form
      onSubmit={handleSubmit}
      className="w-full max-w-4xl mx-auto"
    >

      <div className="rounded-2xl border border-zinc-800 bg-zinc-900 overflow-hidden">

        {/* Solidity textarea */}

        <textarea
          value={contract}

          onChange={(event) =>
            setContract(
              event.target.value
            )
          }

          placeholder="// Paste your Solidity smart contract here..."

          className="
            w-full
            min-h-[400px]
            bg-transparent
            p-6
            font-mono
            text-sm
            text-zinc-200
            outline-none
            resize-none
            placeholder:text-zinc-500
          "
        />


        {/* Bottom controls */}

        <div className="
          flex
          items-center
          justify-between
          gap-4
          border-t
          border-zinc-800
          p-4
        ">

          <div className="flex items-center gap-3">

            {/* Hidden file input */}

            <input
              ref={fileInputRef}

              type="file"

              accept=".sol"

              onChange={handleFileChange}

              className="hidden"

              id="solidity-upload"
            />


            {/* Upload button */}

            <label
              htmlFor="solidity-upload"

              className="
                cursor-pointer
                text-sm
                text-zinc-400
                hover:text-white
                transition
              "
            >

              📎 Upload .sol

            </label>


            {contract && (

              <button
                type="button"

                onClick={handleNewScan}

                className="
                  text-sm
                  text-zinc-500
                  hover:text-red-400
                  transition
                "
              >

                Clear

              </button>

            )}

          </div>


          {/* Analyze button */}

          <button
            type="submit"

            disabled={isLoading}

            className="
              rounded-xl
              bg-white
              px-6
              py-3
              text-sm
              font-medium
              text-black
              transition
              hover:bg-zinc-200
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >

            {isLoading
              ? "Analyzing..."
              : "Analyze Contract →"
            }

          </button>

        </div>

      </div>


      {/* Error message */}

      {error && (

        <div className="
          mt-4
          rounded-lg
          border
          border-red-900
          bg-red-950/30
          p-4
          text-sm
          text-red-400
        ">

          {error}

        </div>

      )}

    </form>

  );
}