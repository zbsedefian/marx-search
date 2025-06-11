import React, { useEffect } from "react";

const PayPalDonateButton = () => {
  useEffect(() => {
    const scriptId = "paypal-donate-sdk";

    const renderButton = () => {
      const container = document.getElementById("donate-button");
      if (container) container.innerHTML = ""; // Clear old buttons

      if (window.PayPal?.Donation) {
        window.PayPal.Donation.Button({
          env: "production",
          hosted_button_id: "KH2PQYNBTFXL4",
          image: {
            src: "https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif",
            alt: "Donate with PayPal button",
            title: "PayPal - The safer, easier way to pay online!",
          },
        }).render("#donate-button");
      }
    };

    // Only add the script if it hasn't already been added
    if (!document.getElementById(scriptId)) {
      const script = document.createElement("script");
      script.id = scriptId;
      script.src = "https://www.paypalobjects.com/donate/sdk/donate-sdk.js";
      script.charset = "UTF-8";
      script.onload = renderButton;
      document.body.appendChild(script);
    } else {
      // If script already exists, just render the button
      renderButton();
    }

    return () => {
      const container = document.getElementById("donate-button");
      if (container) container.innerHTML = ""; // Clean up if unmounted
    };
  }, []);

  return (
    <div id="donate-button-container">
      <div id="donate-button"></div>
    </div>
  );
};

export default PayPalDonateButton;
