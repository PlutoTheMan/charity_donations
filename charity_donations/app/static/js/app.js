document.addEventListener("DOMContentLoaded", function() {
  /**
   * HomePage - Help section
   */
  class Help {
    constructor($el) {
      this.$el = $el;
      this.$buttonsContainer = $el.querySelector(".help--buttons");
      this.$slidesContainers = $el.querySelectorAll(".help--slides");
      this.currentSlide = this.$buttonsContainer.querySelector(".active").parentElement.dataset.id;
      this.init();
    }

    init() {
      this.events();
    }

    events() {
      /**
       * Slide buttons
       */
      this.$buttonsContainer.addEventListener("click", e => {
        if (e.target.classList.contains("btn")) {
          this.changeSlide(e);
        }
      });

      /**
       * Pagination buttons
       */
      this.$el.addEventListener("click", e => {
        if (e.target.classList.contains("btn") && e.target.parentElement.parentElement.classList.contains("help--slides-pagination")) {
          this.changePage(e);
        }
      });
    }

    changeSlide(e) {
      e.preventDefault();
      const $btn = e.target;

      // Buttons Active class change
      [...this.$buttonsContainer.children].forEach(btn => btn.firstElementChild.classList.remove("active"));
      $btn.classList.add("active");

      // Current slide
      this.currentSlide = $btn.parentElement.dataset.id;

      // Slides active class change
      this.$slidesContainers.forEach(el => {
        el.classList.remove("active");

        if (el.dataset.id === this.currentSlide) {
          el.classList.add("active");
        }
      });
    }

    /**
     * TODO: callback to page change event
     */
    async changePage(e) {
      e.preventDefault();
      const page = e.target.dataset.page;

      const response = await fetch("get_institution_page/" + page);
      const institutions = await response.json();

      let parent = document.getElementById("institutions_list")
      parent.innerHTML = ""

      for (let n in institutions){
        let element_institution = document.createElement("li")
        let e = document.createElement("div")
        e.classList.add("col")
        let title = document.createElement("div")
        title.classList.add("title")
        title.innerText = `Fundacja "${institutions[n].name}"`
        e.appendChild(title)
        let subtitle = document.createElement("div")
        subtitle.classList.add("subtitle")
        subtitle.innerText = `Cel i misja: ${institutions[n].description}`
        e.appendChild(subtitle)
        element_institution.appendChild(e)

        let e2 = document.createElement("div")
        e2.classList.add("col")

        let text = document.createElement("div")
        text.classList.add("text")
        let categories = institutions[n].categories.map((item) => { return item }).join(', ')
        text.innerText = categories
        e2.appendChild(text)
        element_institution.appendChild(e2)
        parent.appendChild(element_institution)
      }

    }
  }
  const helpSection = document.querySelector(".help");
  if (helpSection !== null) {
    new Help(helpSection);
  }

  /**
   * Form Select
   */
  class FormSelect {
    constructor($el) {
      this.$el = $el;
      this.options = [...$el.children];
      this.init();
    }

    init() {
      this.createElements();
      this.addEvents();
      this.$el.parentElement.removeChild(this.$el);
    }

    createElements() {
      // Input for value
      this.valueInput = document.createElement("input");
      this.valueInput.type = "text";
      this.valueInput.name = this.$el.name;

      // Dropdown container
      this.dropdown = document.createElement("div");
      this.dropdown.classList.add("dropdown");

      // List container
      this.ul = document.createElement("ul");

      // All list options
      this.options.forEach((el, i) => {
        const li = document.createElement("li");
        li.dataset.value = el.value;
        li.innerText = el.innerText;

        if (i === 0) {
          // First clickable option
          this.current = document.createElement("div");
          this.current.innerText = el.innerText;
          this.dropdown.appendChild(this.current);
          this.valueInput.value = el.value;
          li.classList.add("selected");
        }

        this.ul.appendChild(li);
      });

      this.dropdown.appendChild(this.ul);
      this.dropdown.appendChild(this.valueInput);
      this.$el.parentElement.appendChild(this.dropdown);
    }

    addEvents() {
      this.dropdown.addEventListener("click", e => {
        const target = e.target;
        this.dropdown.classList.toggle("selecting");

        // Save new value only when clicked on li
        if (target.tagName === "LI") {
          this.valueInput.value = target.dataset.value;
          this.current.innerText = target.innerText;
        }
      });
    }
  }
  document.querySelectorAll(".form-group--dropdown select").forEach(el => {
    new FormSelect(el);
  });

  /**
   * Hide elements when clicked on document
   */
  document.addEventListener("click", function(e) {
    const target = e.target;
    const tagName = target.tagName;

    if (target.classList.contains("dropdown")) return false;

    if (tagName === "LI" && target.parentElement.parentElement.classList.contains("dropdown")) {
      return false;
    }

    if (tagName === "DIV" && target.parentElement.classList.contains("dropdown")) {
      return false;
    }

    document.querySelectorAll(".form-group--dropdown .dropdown").forEach(el => {
      el.classList.remove("selecting");
    });
  });

  /**
   * Switching between form steps
   */
  class FormSteps {
    constructor(form) {
      this.$form = form;
      this.$next = form.querySelectorAll(".next-step");
      this.$prev = form.querySelectorAll(".prev-step");
      this.$step = form.querySelector(".form--steps-counter span");
      this.currentStep = 1;
      this.checked_categories = []

      this.$stepInstructions = form.querySelectorAll(".form--steps-instructions p");
      const $stepForms = form.querySelectorAll("form > div");
      this.slides = [...this.$stepInstructions, ...$stepForms];

      this.init();
    }

    /**
     * Init all methods
     */
    init() {
      this.events();
      this.updateForm();
    }

    /**
     * All events that are happening in form
     */
    events() {
      // Next step
      this.$next.forEach(btn => {
        btn.addEventListener("click", e => {
          e.preventDefault();
          this.currentStep++;
          this.updateForm();
        });
      });

      // Previous step
      this.$prev.forEach(btn => {
        btn.addEventListener("click", e => {
          e.preventDefault();
          this.currentStep--;
          this.updateForm();
        });
      });

      // Form submit
      this.$form.querySelector("form").addEventListener("submit", e => this.submit(e));
    }

    /**
     * Update form front-end
     * Show next or previous section etc.
     */
    updateForm() {
      if (this.currentStep == 2) {
        const institutions = document.querySelectorAll(".institution-choice")
        const checked_inputs = document.querySelector("div[data-step='1']").querySelectorAll("input:checked")

        checked_inputs.forEach(e=>{
          this.checked_categories.push(e.value)
        })

        // This step is to reset filter, in case user steps back.
        institutions.forEach(institution=>{
          if (institution.classList.contains("hidden")) {
            institution.classList.remove("hidden")
          }
        })

        institutions.forEach(institution=>{
          const hasAllElems = this.checked_categories.every(elem => institution.dataset.categories.includes(elem));
          if (!hasAllElems) {
            institution.classList.add("hidden")
          }
        })

        const input_categories = document.querySelector("input[name='checked_categories']")
        // console.log(input_categories)
        input_categories.value = JSON.stringify(this.checked_categories)
        console.log(this.checked_categories)
        console.log(input_categories)

      } else if (this.currentStep == 5){
        const bag_count = document.querySelector("div[data-step='2']")
            .querySelector("input").value
        const checked_org =
            document.querySelector("div[data-step='3']")
            .querySelector("input[name=organization]:checked").parentElement
            .querySelector(".title").innerText
        const checked_org_parsed = checked_org.substring(
            checked_org.indexOf('“') + 1,
            checked_org.lastIndexOf('”'),
        )

        const summary_address = document.querySelector("input[name=address]").value
        const summary_city = document.querySelector("input[name=city]").value
        const summary_postcode = document.querySelector("input[name=postcode]").value
        const summary_phone = document.querySelector("input[name=phone]").value

        const summary_data = document.querySelector("input[name=data]").value
        const summary_time = document.querySelector("input[name=time]").value
        const summary_more_info = document.querySelector("textarea[name=more_info]").value

        document.getElementById("summary_bag_count").innerText = bag_count
        document.getElementById("summary_foundation_name").innerText = checked_org_parsed
        document.getElementById("summary_address").innerText = summary_address
        document.getElementById("summary_city").innerText = summary_city
        document.getElementById("summary_postcode").innerText = summary_postcode
        document.getElementById("summary_phone").innerText = summary_phone

        document.getElementById("summary_data").innerText = summary_data
        document.getElementById("summary_time").innerText = summary_time
        document.getElementById("summary_more_info").innerText = summary_more_info
      }

      this.$step.innerText = this.currentStep;

      // TODO: Validation

      this.slides.forEach(slide => {
        slide.classList.remove("active");

        if (slide.dataset.step == this.currentStep) {
          slide.classList.add("active");
        }
      });

      this.$stepInstructions[0].parentElement.parentElement.hidden = this.currentStep >= 6;
      this.$step.parentElement.hidden = this.currentStep >= 6;

    }

    /**
     * Submit form
     *
     * TODO: validation, send data to server
     */
    submit(e) {
      e.preventDefault();
      if (this.currentStep < 5){
        this.currentStep++;
        this.updateForm();
      } else {
        // e.formData.set('categories', this.checked_orgs)
        e.currentTarget.submit()
      }
    }
  }
  const form = document.querySelector(".form--steps");
  if (form !== null) {
    new FormSteps(form);
  }
});
