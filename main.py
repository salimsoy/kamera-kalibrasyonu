import cv2
import numpy as np
import glob

class CameraCalibrate:
    def __init__(self):
        self.CHECKERBOARD = (6, 9)
        self.criteria = (cv2.TERM_CRITERIA_EPS + 
            cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.objpoints = []
        self.imgpoints = []
        self.objectp3d = np.zeros((1, self.CHECKERBOARD[0] 
                              * self.CHECKERBOARD[1], 
                              3), np.float32)
        self.objectp3d[0, :, :2] = np.mgrid[0:self.CHECKERBOARD[0],
                                       0:self.CHECKERBOARD[1]].T.reshape(-1, 2)
        self.prev_img_shape = None
        self.mean_error = 0
        
        

    def camera_calibrate(self):
        images = glob.glob('*.jpg')
        
        for filename in images:
            image = cv2.imread(filename)
            grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
            ret, corners = cv2.findChessboardCorners(
                            grayColor, self.CHECKERBOARD, 
                            cv2.CALIB_CB_ADAPTIVE_THRESH 
                            + cv2.CALIB_CB_FAST_CHECK + 
                            cv2.CALIB_CB_NORMALIZE_IMAGE)
        
        
            if ret == True:
                self.objpoints.append(self.objectp3d)
        
                corners2 = cv2.cornerSubPix(
                    grayColor, corners, (11, 11), (-1, -1), self.criteria)
        
                self.imgpoints.append(corners2)
        
                image = cv2.drawChessboardCorners(image, 
                                                  self.CHECKERBOARD, 
                                                  corners2, ret)
        
            cv2.imshow('img', image)
            cv2.waitKey(0)
        
        cv2.destroyAllWindows()
        ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
            self.objpoints, self.imgpoints, grayColor.shape[::-1], None, None)
        return matrix, distortion, r_vecs, t_vecs
        
    
    def correction(self, img, matrix, distortion):
        h,  w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(matrix, distortion, (w,h), 1, (w,h))
        
        dst = cv2.undistort(img, matrix, distortion, None, newcameramtx)
        
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        cv2.imwrite('output.png', dst)
        
    def calculate_error(self, matrix, distortion, r_vecs, t_vecs):
        for i in range(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], r_vecs[i], t_vecs[i], matrix, distortion)
            error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
            self.mean_error += error
            return imgpoints2
        
        
    def main(self):
        
        matrix, distortion, r_vecs, t_vecs = self.camera_calibrate()
        img = cv2.imread('3.jpg')
        self.correction(img, matrix, distortion)
        imgpoints2 = self.calculate_error(matrix, distortion, r_vecs, t_vecs)
        
        
        print( "toplam hata: {}".format(self.mean_error/len(self.objpoints)) )
        
        
        print("Projeksiyon sonucu 2D noktalar:\n", imgpoints2)
        
        print("\n Kamera matrix:")
        print(matrix)
        
        print("\n distortion:")
        print(distortion)
        
        print("\n rotation Vectors:")
        print(r_vecs)
        
        print("\n translation Vectors:")
        print(t_vecs)


if __name__ == '__main__':

    process = CameraCalibrate()
    process.main()