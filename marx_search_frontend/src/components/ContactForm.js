import React from "react";
import { useForm, ValidationError } from "@formspree/react";

export default function ContactForm({ onClose }) {
  const [state, handleSubmit] = useForm("mdkzgeky");

  if (state.succeeded) {
    return (
      <div className="text-center">
        <p className="text-green-600 dark:text-green-400 font-semibold">
          Thanks for your message!
        </p>
        <button
          onClick={onClose}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Close
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        id="email"
        type="email"
        name="email"
        required
        placeholder="Your email"
        className="w-full p-2 border rounded dark:bg-gray-800 dark:text-white"
      />
      <ValidationError prefix="Email" field="email" errors={state.errors} />

      <textarea
        id="message"
        name="message"
        rows="4"
        required
        placeholder="Your message"
        className="w-full p-2 border rounded dark:bg-gray-800 dark:text-white"
      />
      <ValidationError prefix="Message" field="message" errors={state.errors} />

      <button
        type="submit"
        disabled={state.submitting}
        className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Submit
      </button>
    </form>
  );
}
