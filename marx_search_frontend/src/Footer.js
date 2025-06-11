import React, { useState } from "react";

export default function Footer() {
  const [image, setImage] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <footer className="bg-[#fceedd] dark:bg-[#1e1e1e] text-center py-6 text-gray-600 dark:text-gray-400 font-serif">
      <div className="flex flex-col items-center space-y-3">
        <span>© 2024 Marx Search</span>
        <a href="#" className="text-blue-700 dark:text-blue-400 hover:underline">
          Donate via PayPal
        </a>
        {image && <img src={image} alt="Footer" className="h-16" />}
        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          className="text-gray-800 dark:text-gray-200"
        />
      </div>
    </footer>
  );
}
