const config = {
  "Service": {
    "API_BASE_URL": "http://localhost:8787"
  },
  "AzureOpenAI": {
    "azure_endpoint": "https://xxxxxx.openai.azure.com",
    "api_key": "xxxxxx",
    "api_version": "2024-03-01-preview",
    "model_name": "gpt-4-v",
    "temperature": "1",
    "max_tokens": "4096",
  }
}

const service_url = config.Service.API_BASE_URL;


const $azure_endpoint = $("#azure_endpoint");
const $api_version = $("#api_version");
const $model_name = $("#model_name");
const $api_key = $("#api_key");
const $temperature = $("#temperature");
const $max_tokens = $("#max_tokens");
const $streaming = $("#streaming");
const $user_image = $("#user_image");
const $user_prompt = $("#user_prompt");
const $gpt_response = $("#gpt_response");
const $loading = $("#loading");
const $firstResponseTime = $("#firstResponseTime");
const $processingTime = $("#processingTime");
const $submitButton = $("#submitButton");



$(document).ready(function () {
  // 設定class
  $("input").addClass("form-control mt-2");
  $("select").addClass("form-control mt-2");
  $("textarea").addClass("form-control mt-2");

  // 設定預設值
  fill_default_values();
});

$user_image.on('change', function (e) {
  var file = e.target.files[0];
  var reader = new FileReader();

  reader.onloadend = function () {
    $('#imagePreview').attr('src', reader.result);
  };

  if (file) {
    reader.readAsDataURL(file);
  } else {
    $('#imagePreview').attr('src', "");
  }
});

$submitButton.on("click", function () {
  try {
    $loading.show();

    $gpt_response.text("");
    $gpt_response.val("");
    $processingTime.text("");
    $processingTime.val("");
    $firstResponseTime.text("");
    $firstResponseTime.val("");

    if ($streaming.is(":checked")) {
      get_gpt_response_streaming();
    } else {
      get_gpt_response();
    }
  } catch (error) {
    console.error("Error:", error);
    $loading.hide();
    $gpt_response.val(error);
  }
});

function fill_default_values() {
  $azure_endpoint.val(config.AzureOpenAI.azure_endpoint);
  $api_key.val(config.AzureOpenAI.api_key);
  $api_version.val(config.AzureOpenAI.api_version);
  $model_name.val(config.AzureOpenAI.model_name);
  $temperature.val(config.AzureOpenAI.temperature);
  $max_tokens.val(config.AzureOpenAI.max_tokens);
}


function upload_image() {
  return new Promise((resolve, reject) => {
    if ($user_image[0].files.length === 0) {
      resolve(null);
    } else {
      const formData = new FormData();
      formData.append("user_image", $user_image[0].files[0]);

      fetch(`${service_url}/save_user_image`, {
        method: "POST",
        body: formData,
      })
        .then(response => response.json())
        .then(res => {
          if (res) {
            resolve(res.hashed_file_name);
          } else {
            reject(res);
          }
        });
    }
  });
}

function get_gpt_response() {
  const start = new Date().getTime();
  const formData = new FormData();
  formData.append("azure_endpoint", $azure_endpoint.val());
  formData.append("api_version", $api_version.val());
  formData.append("model_name", $model_name.val());
  formData.append("api_key", $api_key.val());
  formData.append("temperature", $temperature.val());
  formData.append("max_tokens", $max_tokens.val());
  formData.append("image", $user_image[0].files[0]);
  formData.append("user_prompt", $user_prompt.val());

  fetch(`${service_url}/get_gpt_response`, {
    method: "POST",
    body: formData,
  })
    .then(response => response.json())
    .then(res => {
      $loading.hide();

      if (res.data) {
        $gpt_response.val(res.data.response);
      } else if (res.error) {
        $gpt_response.val(res.error);
      } else {
        $gpt_response.val(res);
      }

      const end = new Date().getTime();
      const time = end - start;
      $processingTime.text(Number(time / 1000).toFixed(0) + " 秒");
      $firstResponseTime.text(Number(time / 1000).toFixed(0) + " 秒");
    })
    .catch(error => {
      console.error("Error:", error);
      $loading.hide();
      $gpt_response.val(error);
    });
}

function get_gpt_response_streaming() {
  let hashed_file_name;

  upload_image().then(res => {
    hashed_file_name = res;
    let eventSource;

    const start = new Date().getTime();
    let firstResponse = false;

    if (!eventSource) {
      const params = {
        azure_endpoint: $azure_endpoint.val(),
        api_version: $api_version.val(),
        model_name: $model_name.val(),
        api_key: $api_key.val(),
        temperature: $temperature.val(),
        max_tokens: $max_tokens.val(),
        user_prompt: $user_prompt.val(),
      };

      if (hashed_file_name) {
        params["hashed_file_name"] = hashed_file_name;
      }

      const queryString = new URLSearchParams(params).toString();
      eventSource = new EventSource(`${service_url}/get_gpt_response_streaming?${queryString}`);
      eventSource.onmessage = function (event) {
        res_data = JSON.parse(event.data);
        if (!firstResponse && res_data !== 'None' && res_data !== '') {
          firstResponse = true;
          $loading.hide();
          let first_response_time = new Date().getTime();
          let time = first_response_time - start;
          $firstResponseTime.text(Number(time / 1000).toFixed(0) + " 秒");

          $gpt_response.val($gpt_response.val() + res_data);
        } else if (res_data !== 'None' && res_data !== '' && res_data !== 'End of stream') {

          $gpt_response.val($gpt_response.val() + res_data);
        } else if (res_data.trim() === 'End of stream') {
          eventSource.close();
          eventSource = null;
          $processingTime.text(Number((new Date().getTime() - start) / 1000).toFixed(0) + " 秒");
        }
      };

      eventSource.onerror = function (error) {
        console.error("Error:", error);
        $gpt_response.val("伺服器錯誤");
        $loading.hide();
        eventSource.close();
        eventSource = null;
      };
    }
  }).catch(error => {
    console.error("Error:", error);
    $loading.hide();
    $gpt_response.val(error);
  });
}
