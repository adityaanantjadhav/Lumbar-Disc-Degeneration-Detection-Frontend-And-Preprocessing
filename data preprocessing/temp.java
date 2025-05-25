
package com.FinalYear.controller;


import com.FinalYear.Dto.DoctorResponseDto;
import com.FinalYear.Dto.ResultResponseDto;
import com.FinalYear.entity.Result;
import com.FinalYear.service.AppService;
import com.FinalYear.entity.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@CrossOrigin(origins = "http://127.0.0.1:5500")
public class AppController {


    @Autowired
    AppService appService;

    @GetMapping()
    public ResponseEntity<?> getUser(int userId){
        return null;
    }

    @PostMapping()
    public ResponseEntity<?> createUser(@RequestBody User user){
        return null;
    }


    @PostMapping("/analyse-image")
    public ResponseEntity<?> analyseImage(@RequestParam("file") MultipartFile file,
                                          @RequestParam("userId") String userId,
                                          @RequestParam("viewType") String viewType) throws IOException {

        File tempFile = File.createTempFile("upload_", file.getOriginalFilename());
        file.transferTo(tempFile);



        Long resultId=appService.analyseImage(userId,tempFile,viewType);

        Map<String,Long> map=new HashMap<>();
        map.put("resultId",resultId);
        tempFile.delete();

        if(resultId==-1)
                return new ResponseEntity<>("Some error occured",HttpStatus.INTERNAL_SERVER_ERROR);
        return new ResponseEntity<Map<String, Long>>(map, HttpStatus.OK);
    }

    @GetMapping("/get-result/{resultId}")
    public ResponseEntity<?> getResult(@PathVariable Long resultId){
        return new ResponseEntity<ResultResponseDto>(appService.getResult(resultId),HttpStatus.OK);
    }


    @GetMapping("/get-image/{resultId}")
    public ResponseEntity<?> getImage(@PathVariable Long resultId) throws IOException {
        return appService.getImage(resultId);
    }

    @GetMapping("/get-doctors-city")
    public ResponseEntity<?> getDoctorsByCity(@RequestParam String city){
        return new ResponseEntity<List<DoctorResponseDto>>(appService.getDoctorsByCity(city),HttpStatus.OK);
    }

    @GetMapping("/get-doctors-pincode")
    public ResponseEntity<?> getDoctorsByPincode(@RequestParam int pincode){
        return new ResponseEntity<List<DoctorResponseDto>>(appService.getDoctorsByPincode(pincode),HttpStatus.OK);
    }


    @PostMapping("/mail-results")
    public ResponseEntity<?> mailResults(@RequestParam String email,@RequestParam Long resultId){
        int index=email.indexOf('@');
        if(index==-1 || (!email.substring(index+1).equals("gmail.com")&& !email.substring(index+1).equals("yahoo.com")&&!email.substring(index+1).equals("outlook.com"))){
            return new ResponseEntity<String>("Wrong email entered",HttpStatus.BAD_REQUEST);
        }

        appService.mailResult(email,resultId);
        return new ResponseEntity<String>("Mail Successfully sent",HttpStatus.OK);
    }


    @GetMapping("/get-previous-results")
    public ResponseEntity<?> getPreviousResults(@RequestParam String userEmail){
        return new ResponseEntity<List<ResultResponseDto>>(appService.getPreviousResults(userEmail),HttpStatus.OK);
    }

}
