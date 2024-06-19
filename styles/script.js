let scrollAmount = 0; // 用於 MRT 列表的滾動位置
let currentPage = 0; // 當前加載的頁面
let loading = false; // 標誌是否正在加載數據
let keyword = ""; // 當前的搜索關鍵字
let nextPage = 1; // 初始為第一頁
let currentOffset = 0; // 用於 MRT 列表的滾動偏移

document.addEventListener("DOMContentLoaded", () => {
  // 向左滾動 MRT 列表
  function scrollLeft() {
    const container = document.querySelector(".listbar");
    const content = document.querySelector(".listbar-inner");

    currentOffset -= container.clientWidth / 3;
    if (currentOffset < 0) {
      currentOffset = content.scrollWidth - container.clientWidth;
    }
    updateScrollPosition();
  }

  // 向右滾動 MRT 列表
  function scrollRight() {
    const container = document.querySelector(".listbar");
    const content = document.querySelector(".listbar-inner");

    currentOffset += container.clientWidth / 3;
    if (currentOffset >= content.scrollWidth - container.clientWidth) {
      currentOffset = 0;
    }
    updateScrollPosition();
  }

  function updateScrollPosition() {
    const container = document.querySelector(".listbar-inner");
    container.style.transform = `translateX(-${currentOffset}px)`;
  }

  document.querySelector(".left-arrow").addEventListener("click", scrollLeft);
  document.querySelector(".right-arrow").addEventListener("click", scrollRight);

  // 使用 fetch 從 API 獲取 MRT 資料並插入到 HTML 中
  fetch("/api/mrts")
    .then((response) => response.json())
    .then((data) => {
      const mrtStations = data.data;
      const container = document.getElementById("mrt-stations");

      function populateStations() {
        container.innerHTML = "";
        mrtStations.forEach((stationName) => {
          const station = document.createElement("div");
          station.className = "station";
          station.textContent = stationName;
          station.style.cursor = "pointer"; // 設置鼠標樣式
          station.addEventListener("mouseover", () => {
            station.style.color = "black"; // 設置懸停字體顏色
          });
          station.addEventListener("mouseout", () => {
            station.style.color = ""; // 恢復原始字體顏色
          });
          station.addEventListener("click", () => {
            document.getElementById("search-input").value = station.textContent;
            keyword = station.textContent;
            currentPage = 0;
            nextPage = 1;
            fetchAttractions(currentPage, keyword, true);
          });
          container.appendChild(station);
        });

        // 克隆節點以實現無限滾動
        for (let i = 0; i < 2; i++) {
          mrtStations.forEach((stationName) => {
            const station = document.createElement("div");
            station.className = "station";
            station.textContent = stationName;
            station.style.cursor = "pointer"; // 設置鼠標樣式
            station.addEventListener("mouseover", () => {
              station.style.color = "black"; // 設置懸停字體顏色
            });
            station.addEventListener("mouseout", () => {
              station.style.color = ""; // 恢復原始字體顏色
            });
            station.addEventListener("click", () => {
              document.getElementById("search-input").value =
                station.textContent;
              keyword = station.textContent;
              currentPage = 0;
              nextPage = 1;
              fetchAttractions(currentPage, keyword, true);
            });
            container.appendChild(station);
          });
        }
      }

      populateStations();
    })
    .catch((error) => console.error("fetching MRT stations Error", error)); // 錯誤處理

  // 確保搜索功能正常工作
  document.getElementById("search-button").addEventListener("click", () => {
    keyword = document.getElementById("search-input").value;
    currentPage = 0;
    nextPage = 1;
    fetchAttractions(currentPage, keyword, true);
  });

  // // 獲取景點數據的函數
  function fetchAttractions(page = 0, keyword = "", reset = false) {
    if (loading) return; // 防止重複請求
    loading = true; // 標誌正在加載數據
    let url = `/api/attractions?page=${page}`;
    if (keyword) {
      url += `&keyword=${keyword}`;
    }

    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        const attractionsContainer =
          document.getElementById("attractions_group");
        if (reset) {
          attractionsContainer.innerHTML = ""; // 清空已有的數據
        }

        data.data.forEach((attraction) => {
          const div = document.createElement("div");
          div.className = "attraction";
          div.innerHTML = `
          <div id="desktop_attraction">
            <img class="desktop_attraction_img" src="${attraction.images[0]}" alt="${attraction.name}">
            <div class="name_outline">
              <div class="name">${attraction.name}</div>
            </div>
            <div class="mrtandcategory_outline">
              <div class="mrtandcategory">${attraction.mrt}</div>
              <div class="mrtandcategory">${attraction.category}</div>
            </div>
          </div>
        `;
          attractionsContainer.appendChild(div);
        });

        nextPage = data.nextPage; // 更新下一頁的頁碼
        loading = false; // 完成加載

        // 在加載新數據後觀察最後一個景點
        if (nextPage !== null) {
          observeLastAttraction();
        }
      })
      .catch((error) => {
        console.error("Error fetching attractions:", error); // 錯誤處理
        loading = false; // 加載失敗，重置標誌
      });
  }

  // 初始加載第一頁數據
  fetchAttractions(currentPage, keyword, true);

  // 使用 IntersectionObserver 觀察頁面底部標記
  function observeLastAttraction() {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loading && nextPage !== null) {
          // 延遲1秒鐘後加載下一頁數據
          setTimeout(() => {
            fetchAttractions(nextPage, keyword);
          }, 1350);
          observer.disconnect(); // 加載後斷開觀察，避免多次觸發
        }
      },
      {
        root: null,
        rootMargin: "0px",
        threshold: 1.0, // 確保滾動到底部時才觸發
      }
    );

    const lastAttraction = document.querySelector(".attraction:last-child");
    if (lastAttraction) {
      observer.observe(lastAttraction);
    }
  }
});
