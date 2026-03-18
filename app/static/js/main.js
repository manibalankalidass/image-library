
function submitSingle() {

    var file = document.getElementById("singleInput").files[0];

    if (!file) {
        toast("Please select image", "error");
        return;
    }

    var formData = new FormData();

    formData.append("image", file);
    formData.append("name", $("#singleName").val());
    formData.append("category", $("#singleCategory").val());
    formData.append("country", $("#countrySelect").val());
    formData.append("description", $("#singleDesc").val());

    // collect tags
    var tags = [];
    $("#tagList span").each(function () {
        tags.push($(this).text());
    });

    formData.append("tags", tags.join(","));

    $.ajax({

        url: "/upload-image",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,

        xhr: function () {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener("progress", function (evt) {

                if (evt.lengthComputable) {

                    var percent = Math.round((evt.loaded / evt.total) * 100);

                    $("#singleProgress").show();
                    $("#singlePct").text(percent + "%");
                    $("#singleFill").css("width", percent + "%");

                }

            }, false);

            return xhr;
        },

        success: function (res) {

            $("#singleStatus").text("Upload complete");

            toast("Image uploaded successfully", "success");
            resetSingle();

        },

        error: function () {
            toast("Upload failed", "error");
        }

    });

}


function handleSingleFile(file) {

    if (!file) return;

    $('#singleDrop').addClass('has-file');
    $('#singleDropInner').html(`
        <div style="font-size:36px;">🖼</div>
        <div style="font-size:15px;font-weight:600;margin-top:8px;">${file.name}</div>
        <div style="font-size:12px;color:var(--muted);margin-top:4px;">
            ${formatBytes(file.size)} &middot; <button type="button" class="btn btn-ghost" style="border: 1px solid #ccc; padding: 2px 6px; font-size: 11px;" onclick="removeSingleFile(event)">Remove</button>
        </div>
    `);

    document.getElementById("previewCard").style.display = "none";

    checkSingleValidity();

}


function switchTab(type, btn) {

    $(".tab-btn").removeClass("active");
    $(btn).addClass("active");

    $(".panel").stop(true, true).fadeOut(150);

    $("#panel-" + type).stop(true, true).fadeIn(200);
}


function uploadZipImages() {

    let zipFile = $("#zipInput")[0].files[0];

    if (!zipFile) {
        toast("Please select a ZIP file", "error");
        return;
    }

    let formData = new FormData();
    formData.append("category", $("#bulkDefaultCat").val());
    formData.append("country", $("#bulkDefaultCountry").val());
    formData.append("zipfile", zipFile);

    $.ajax({
        url: "/upload-zip",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function () {
            $("#uploadStatus").text("Uploading ZIP...");
        },
        success: function (response) {

            $("#uploadStatus").text("Upload Completed");
            toast("Images uploaded successfully", "success");
            resetBulk();
        },
        error: function (xhr) {
            toast("Upload failed", "error");
        }
    });

}



function handleZipFile(file) {

    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.zip')) {
        toast('Please select a .zip file', 'error');
        return;
    }

    if (file.size > 200 * 1024 * 1024) {
        toast('ZIP exceeds 200 MB limit', 'error');
        return;
    }

    zipFile = file;

    // Simulate scanning ZIP
    // simulateZipScan(file);
}


function simulateZipScan(file) {

    const count = Math.floor(Math.random() * 16) + 6;
    const folders = ['nature', 'architecture', 'people', 'technology', 'abstract'];
    const names = ['sunset', 'cityscape', 'portrait', 'circuit', 'splash', 'mountain', 'bridge', 'crowd', 'server', 'bloom', 'tower', 'skyline', 'gradient', 'waterfall', 'alley', 'neon'];
    const exts = ['jpg', 'jpg', 'jpg', 'png', 'webp', 'png', 'jpeg', 'gif'];

    zipEntries = [];
    let totalSize = 0;

    for (let i = 0; i < count; i++) {

        const folder = folders[Math.floor(Math.random() * folders.length)];
        const name = names[Math.floor(Math.random() * names.length)] + '_' + (i + 1);
        const ext = exts[Math.floor(Math.random() * exts.length)];
        const size = Math.floor(Math.random() * 3500000) + 200000;
        const valid = Math.random() > 0.1;

        totalSize += size;

        zipEntries.push({
            folder: folder,
            name: name + '.' + ext,
            fullName: folder + '/' + name + '.' + ext,
            size: size,
            valid: valid,
            status: valid ? 'pending' : 'skip'
        });
    }

    // Add invalid files
    zipEntries.push({ folder: 'misc', name: 'readme.txt', fullName: 'readme.txt', size: 1200, valid: false, status: 'skip' });
    zipEntries.push({ folder: 'misc', name: 'thumbs.db', fullName: 'thumbs.db', size: 4096, valid: false, status: 'skip' });

    const validCount = zipEntries.filter(e => e.valid).length;
    const skippedCount = zipEntries.filter(e => !e.valid).length;

    // Update UI (jQuery)
    $('#zipSummaryWrap').show();
    $('#zipTotalFiles').text(zipEntries.length);
    $('#zipValidFiles').text(validCount);
    $('#zipSkippedFiles').text(skippedCount);
    $('#zipTotalSize').text(formatBytes(totalSize));
    $('#zipFileCountBadge').text(zipEntries.length + ' files');

    // Update drop zone
    $('#zipDrop').addClass('has-file');

    $('#zipDropInner').html(`
        <div style="font-size:36px;">✅</div>
        <div style="font-size:15px;font-weight:600;margin-top:8px;">${file.name}</div>
        <div style="font-size:12px;color:var(--muted);margin-top:4px;">
            ${formatBytes(file.size)} &middot; ${zipEntries.length} files found &middot; <button type="button" class="btn btn-ghost" style="border: 1px solid #ccc; padding: 2px 6px; font-size: 11px;" onclick="removeZipFile(event)">Remove</button>
        </div>
    `);

    checkBulkValidity();
    toast(`ZIP scanned — ${validCount} images found`, 'info');
}






function selectCountry(element, country = 'uk') {

    $(".standard-btn").removeClass("selected");

    $(element).addClass("selected");

    // let country = $(element).data("country");

    $("#country_selected").val(country);

}


function saveCategory() {

    let categoryName = $("#category_name").val().trim();
    let country = $("#country_selected").val();

    if (categoryName === "") {

        toast("Category name is required", "error");
        return;

    }

    let payload = {
        name: categoryName,
        country: country
    };

    sendCategoryRequest(payload);

}


function sendCategoryRequest(data) {

    $.ajax({

        url: "/categories/create",

        type: "POST",

        contentType: "application/json",

        data: JSON.stringify(data),

        success: function (response) {

            handleSuccess(response);

        },

        error: function (xhr) {

            handleError(xhr);

        }

    });

}


function handleSuccess(response) {

    toast("Category saved successfully", "success");

    resetCategoryForm();

}


function handleError(error) {

    toast("Error saving category", "error");

}


function resetCategoryForm() {

    $("#category_name").val("");

    $(".standard-btn").removeClass("selected");

    $(".standard-btn[data-country='UK']").addClass("selected");

    $("#country_selected").val("UK");

}

function toast(message, type = 'info') {
    const bg = type === 'error' ? '#ff4d4d' : (type === 'success' ? '#4caf50' : '#2196f3');
    const $toast = $(`<div style="background:${bg};color:#fff;padding:12px 20px;border-radius:4px;margin-bottom:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);z-index:9999;position:relative;">${message}</div>`);
    $('#toastContainer').append($toast);
    setTimeout(() => {
        $toast.fadeOut(400, function () { $(this).remove(); });
    }, 3000);
}

function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

function resetSingle() {
    removeSingleFile();
    $("#singleName, #singleCategory, #countrySelect, #singleDesc").val("");
    $("#singleSubmitBtn").prop("disabled", true);
}

function resetBulk() {
    removeZipFile();
    $("#bulkDefaultCat, #bulkDefaultCountry").val("");
    $("#bulkSubmitBtn").prop("disabled", true);
}

function removeSingleFile(e) {
    if (e) {
        e.stopPropagation();
        e.preventDefault();
    }
    $("#singleInput").val("");
    $('#singleDrop').removeClass('has-file');
    $('#singleDropInner').html(`
        <div class="drop-icon">🏔</div>
        <div class="drop-title">Drop your image here</div>
        <div class="drop-sub">or <span class="browse-link">browse files</span> from your device</div>
        <div class="drop-formats">
            <span class="fmt-chip">JPG</span>
            <span class="fmt-chip">PNG</span>
            <span class="fmt-chip">WEBP</span>
            <span class="fmt-chip">GIF</span>
            <span class="fmt-chip">SVG</span>
            <span class="fmt-chip">Max 10 MB</span>
        </div>
    `);
    document.getElementById("previewCard").style.display = "none";
    checkSingleValidity();
}

function removeZipFile(e) {
    if (e) {
        e.stopPropagation();
        e.preventDefault();
    }
    $("#zipInput").val("");
    $('#zipDrop').removeClass('has-file');
    $('#zipDropInner').html(`
        <div class="drop-icon">📦</div>
        <div class="drop-title">Drop your ZIP here</div>
        <div class="drop-sub">or <span class="zip-browse-link">browse files</span> from your device</div>
        <div class="drop-formats">
            <span class="fmt-chip" style="border-color:#6e8eff40;color:var(--accent2);">.ZIP</span>
            <span class="fmt-chip">JPG inside</span>
            <span class="fmt-chip">PNG inside</span>
            <span class="fmt-chip">Max 200 MB</span>
        </div>
    `);
    $('#zipSummaryWrap').hide();
    checkBulkValidity();
}

function checkSingleValidity() {
    let fileElem = document.getElementById("singleInput");
    let file = fileElem && fileElem.files ? fileElem.files[0] : null;
    let cat = $("#singleCategory").val();
    if (file && cat) {
        $("#singleSubmitBtn").prop("disabled", false);
    } else {
        $("#singleSubmitBtn").prop("disabled", true);
    }
}

function checkBulkValidity() {
    let fileElem = document.getElementById("zipInput");
    let file = fileElem && fileElem.files ? fileElem.files[0] : null;
    let cat = $("#bulkDefaultCat").val();
    if (file && cat) {
        $("#bulkSubmitBtn").prop("disabled", false);
    } else {
        $("#bulkSubmitBtn").prop("disabled", true);
    }
}



