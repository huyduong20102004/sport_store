document.addEventListener("DOMContentLoaded", function(){
  // attach add-to-cart buttons
  document.querySelectorAll(".add-btn").forEach(btn=>{
    btn.addEventListener("click", async (e)=>{
      const id = btn.dataset.id;
      const qtyEl = document.getElementById(`qty-${id}`);
      const qty = qtyEl ? parseInt(qtyEl.value||1) : 1;
      try {
        const resp = await fetch("/add_to_cart", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({product_id: id, qty: qty})
        });
        const data = await resp.json();
        if(resp.status === 200 && data.success){
          alert("Đã thêm vào giỏ hàng");
          // optionally update cart count
          location.reload();
        } else if (resp.status === 403){
          // not logged in
          if(data && data.error) alert(data.error);
          window.location.href = "/login";
        } else {
          alert(data.error || "Lỗi khi thêm giỏ hàng");
        }
      } catch(err){
        alert("Lỗi mạng");
      }
    });
  });

  // optional: intercept contact form
  const contactForm = document.querySelector(".contact-form");
  if(contactForm){
    contactForm.addEventListener("submit", (e)=>{
      e.preventDefault();
      alert("Cảm ơn! (demo) Chúng tôi sẽ liên hệ bạn sớm.");
      contactForm.reset();
    });
  }
});
