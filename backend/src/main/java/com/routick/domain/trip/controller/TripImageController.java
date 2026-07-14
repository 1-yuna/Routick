package com.routick.domain.trip.controller;

import com.routick.domain.trip.entity.TripImage;
import com.routick.domain.trip.repository.TripImageRepository;
import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class TripImageController {

    private final TripImageRepository tripImageRepository;

    @GetMapping("/images/trip/{id}")
    public ResponseEntity<byte[]> get(@PathVariable Long id) {
        TripImage image = tripImageRepository.findById(id)
                .orElseThrow(() -> new CustomException(ErrorCode.IMAGE_UPLOAD_FAILED));
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(image.getContentType()))
                .body(image.getData());
    }
}