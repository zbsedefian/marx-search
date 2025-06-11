import { useState } from "react";
import PayPalDonateButton from "./PayPalDonateButton";
import ContactForm from "./ContactForm";

export default function Footer() {
  const [open, setOpen] = useState(false);
  return (
    <>
<footer className="bg-[#fceedd] dark:bg-[#1e1e1e] text-center py-10 text-gray-700 dark:text-gray-300 font-serif border-t border-gray-300 dark:border-gray-700">
  <div className="flex flex-col items-center space-y-4 max-w-xl mx-auto">

    <span className="text-sm text-gray-500 dark:text-gray-400">
      © 2025 <strong>Marx Search</strong>
    </span>

    <button
      onClick={() => setOpen(true)}
      className="text-sm text-blue-800 dark:text-blue-300 hover:underline transition"
    >
      Contact me to suggest features or report bugs
    </button>

    <div className="pt-2 text-base font-medium">
      Please support this project:
    </div>

    <PayPalDonateButton />

  </div>
</footer>

      {open && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center px-4">
          <div className="bg-white dark:bg-[#1e1e1e] p-6 rounded-xl max-w-md w-full shadow-xl relative">
            <button
              onClick={() => setOpen(false)}
              className="absolute top-2 right-4 text-gray-500 hover:text-red-500 text-xl"
            >
              ✕
            </button>
            <h2 className="text-xl font-bold mb-4">Send a Message</h2>
            <ContactForm onClose={() => setOpen(false)} />
          </div>
        </div>
      )}
    </>
  );
}
